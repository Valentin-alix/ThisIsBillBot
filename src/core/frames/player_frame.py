from dataclasses import dataclass, field
from datetime import UTC, datetime
from threading import Timer

from datas.protos.non_obf.game.account_pb2 import AccountInformationUpdateEvent
from datas.protos.non_obf.game.character_management_pb2 import (
    CharacterSelectionEvent,
)
from datas.protos.non_obf.game.character_pb2 import (
    CharacterCharacteristicUpgradeRequest,
    CharacterLevelUpEvent,
)
from datas.protos.non_obf.game.dialog_pb2 import DialogLeaveRequest
from datas.protos.non_obf.game.gamemap_pb2 import (
    FightMapInformationEvent,
    MapComplementaryInformationEvent,
)
from datas.protos.non_obf.game.job_pb2 import (
    JobExperiencesUpdateEvent,
)
from datas.protos.non_obf.game.teleportation_pb2 import (
    ZaapKnownListEvent,
)

from src.core.engine.fights.stats.characteristic import get_max_characteristic_per_point
from src.core.events_manager.priority import PriorityEnum
from src.core.frames.frame import Frame


@dataclass
class PlayerFrame(Frame):
    _timer: Timer | None = field(init=False, default=None)

    def __post_init__(self):
        self.event_manager.on(
            JobExperiencesUpdateEvent,
            self.on_job_experiences_update_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            AccountInformationUpdateEvent,
            self.on_account_information_update_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            CharacterSelectionEvent,
            self.on_character_selection_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            ZaapKnownListEvent,
            self.on_zaap_known_list_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            CharacterLevelUpEvent, self.on_character_level_up_event, originator=self
        )
        self.event_manager.before(
            DialogLeaveRequest,
            self.before_dialog_leave_request,
            originator=self,
        )

        self.game_info_signals.connected.connect(self.on_connected)
        self.game_info_signals.disconnected.connect(self.on_disconnected)
        self.game_info_signals.is_ready_to_play.connect(
            self.game_state.player.is_ready_to_play_event.set
        )

    def on_connected(self):
        def on_map_init_after_connected():
            self.run_timer(3, self.game_info_signals.is_ready_to_play.emit)
            self.unregister_listener(MapComplementaryInformationEvent)
            self.unregister_listener(FightMapInformationEvent)

        self.event_manager.on(
            MapComplementaryInformationEvent,
            lambda _: on_map_init_after_connected(),
            originator=self,
            once=True,
            priority=PriorityEnum.MAX,
        )
        self.event_manager.on(
            FightMapInformationEvent,
            lambda _: on_map_init_after_connected(),
            originator=self,
            once=True,
            priority=PriorityEnum.MAX,
        )

    def on_disconnected(self):
        self.game_state.player.is_ready_to_play_event.clear()

    def on_character_level_up_event(self, msg: CharacterLevelUpEvent):
        self.game_state.player.level = msg.new_level
        if self.is_playing_event.is_set():
            chance = get_max_characteristic_per_point(msg.new_level)
            self.logger.info(f"New amount of base chance : {chance}")
            req = CharacterCharacteristicUpgradeRequest(chance=chance)
            self.event_manager.send(req)

    def on_job_experiences_update_event(self, message: JobExperiencesUpdateEvent):
        for job_xp in message.experiences:
            # round to ten digit lower bc only that matters
            self.game_state.player.jobs_lvl_by_id[job_xp.job_id] = max(
                (job_xp.job_level // 10) * 10, 1
            )

    def on_account_information_update_event(self, msg: AccountInformationUpdateEvent):
        timestamp = msg.subscription_end_date
        self.game_state.player.subscription_end_date = datetime.fromtimestamp(
            timestamp, tz=UTC
        )

    def on_character_selection_event(self, message: CharacterSelectionEvent):
        if message.HasField("success"):
            self.game_state.player.character_id = message.success.character.id
            self.game_info_signals.connected.emit()
            if message.success.character.HasField("character_basic_information"):
                self.game_state.player.level = (
                    message.success.character.character_basic_information.level
                )
                self.game_state.player.character_name = (
                    message.success.character.character_basic_information.name
                )
                if message.success.character.character_basic_information.HasField(
                    "character_look"
                ):
                    self.game_state.fight.breed_id = message.success.character.character_basic_information.character_look.breed_id
            elif message.success.character.HasField("character_remodeling_information"):
                self.game_state.fight.breed_id = (
                    message.success.character.character_remodeling_information.breed_id
                )

    def on_zaap_known_list_event(self, msg: ZaapKnownListEvent):
        self.game_state.player.waypoint_map_ids = list(msg.destinations)

    def before_dialog_leave_request(self, msg: DialogLeaveRequest):
        if self.is_playing_event.is_set():
            self.logger.info("Cancel dialog leave request from client")
            return None
        return msg
