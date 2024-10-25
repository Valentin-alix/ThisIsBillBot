from dataclasses import dataclass

from d3_mapping.resources.protos.game.character_pb2 import CharacterLifeStatusEvent
from d3_mapping.resources.protos.game.gamemap_pb2 import (
    FightMapInformationEvent,
    MapComplementaryInformationEvent,
    MapCurrentEvent,
    MapMovementConfirmRequest,
)
from data_center.data_reader import DataReader

from src.core.frames.frame import Frame
from src.signals.world_signals import WorldSignals


@dataclass
class MapFrame(Frame):
    world_signals: WorldSignals

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
            CharacterLifeStatusEvent,
            self.on_character_life_status_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            FightMapInformationEvent,
            self.on_fight_map_information_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.before(
            MapMovementConfirmRequest,
            self.before_map_movement_confirm_request,
            originator=self,
        )

    def on_map_complementary_information_event(
        self, message: MapComplementaryInformationEvent
    ):
        self.logger.info(f"New map : {message.map_id}")
        self.game_state.map.map_id = message.map_id
        self.game_state.map.is_in_haven_bag = message.HasField("haven_bag_information")
        self.world_signals.curr_map_pos.emit(
            DataReader().map_pos_by_map_id[message.map_id]
        )
        self.game_state.map.is_in_map_transition = False

    def on_map_current_event(self, msg: MapCurrentEvent):
        self.game_state.map.map_id = msg.map_id
        self.game_state.entity.clear_actors()
        self.game_state.entity.clear_obstacles()
        self.game_state.interactive.clear_stated_elements()
        self.game_state.map.is_in_map_transition = True

    def on_character_life_status_event(self, msg: CharacterLifeStatusEvent):
        self.game_state.map.phoenix_map_id = msg.phoenix_map_id

    def on_fight_map_information_event(self, msg: FightMapInformationEvent):
        self.game_state.map.is_in_haven_bag = False
        self.game_state.fight.is_map_fight_initialized = True
        self.game_state.map.is_in_map_transition = False

    def before_map_movement_confirm_request(self, msg: MapMovementConfirmRequest):
        self.logger.info(
            f"Before map movement confirm request, is playing: {self.is_playing_event.is_set()}"
        )
        if self.is_playing_event.is_set():
            return None
        return msg
