from dataclasses import dataclass, field

from datas.protos.non_obf.game.character_pb2 import PlayerStatusUpdateRequest
from datas.protos.non_obf.game.common_pb2 import CharacterStatus
from datas.protos.non_obf.game.context_pb2 import (
    ContextCreationEvent,
    ContextReadyRequest,
)
from datas.protos.non_obf.game.gamemap_pb2 import (
    FightMapInformationEvent,
    MapChangeRequest,
    MapComplementaryInformationEvent,
    MapCurrentEvent,
    MapInformationRequest,
    MapMovementConfirmRequest,
)
from dofus_unity_reader.data_center.data_reader import DataReader

from src.core.frames.frame import Frame
from src.core.signals.world_signals import WorldSignals


@dataclass
class MapFrame(Frame):
    world_signals: WorldSignals
    _need_context_ready: bool = field(init=False, default=False)

    def __post_init__(self):
        self.game_info_signals.disconnected.connect(self.game_state.map.clear_state)
        self.event_manager.on(
            MapComplementaryInformationEvent,
            self.on_map_complementary_information_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            MapCurrentEvent,
            self.on_map_current_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            FightMapInformationEvent,
            self.on_fight_map_information_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            ContextCreationEvent,
            self.on_context_creation_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.before(
            MapMovementConfirmRequest,
            self.before_map_movement_confirm_request,
            originator=self,
        )
        self.event_manager.before(
            MapChangeRequest,
            self.before_map_change_request,
            originator=self,
        )

    def on_map_complementary_information_event(
        self, message: MapComplementaryInformationEvent
    ):
        self.logger.info(f"New map : {message.map_id}")
        assert self.game_state.map.map_id == message.map_id
        self.game_state.map.is_in_haven_bag = message.HasField("haven_bag_information")
        self.world_signals.curr_map_pos.emit(
            DataReader().map_pos_by_map_id[message.map_id]
        )
        self.game_state.map.is_in_map_transition = False

    def on_context_creation_event(self, msg: ContextCreationEvent) -> None:
        if msg.context == ContextCreationEvent.GameContext.FIGHT:
            self._need_context_ready = True
        if self.event_manager.is_socket_mode:
            self.event_manager.send(
                PlayerStatusUpdateRequest(
                    status=CharacterStatus(status=CharacterStatus.Status.STATUS_SOLO)
                )
            )

    def on_map_current_event(self, msg: MapCurrentEvent):
        self.game_state.map.map_id = msg.map_id
        self.game_state.entity.clear_actors()
        self.game_state.entity.clear_obstacles()
        self.game_state.interactive.clear_stated_elements()
        self.game_state.map.is_in_map_transition = True
        if not self.event_manager.is_socket_mode:
            return
        self.event_manager.send(MapInformationRequest(map_id=msg.map_id))
        if self._need_context_ready:
            self.event_manager.send(ContextReadyRequest(map_id=msg.map_id))
            self._need_context_ready = False

    def on_fight_map_information_event(self, msg: FightMapInformationEvent):
        self.game_state.map.is_in_haven_bag = False
        self.game_state.map.is_in_map_transition = False

    def before_map_movement_confirm_request(self, msg: MapMovementConfirmRequest):
        if self.is_playing_event.is_set():
            self.logger.info(
                "Canceling client map movement confirm response to avoid duplicate"
            )
            return None
        return msg

    def before_map_change_request(self, msg: MapChangeRequest):
        if not self.game_state.player.is_sub:
            self.logger.info("Altering map change request auto_pilot set to False")
            msg.auto_pilot = False
        return msg
