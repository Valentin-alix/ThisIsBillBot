from dataclasses import dataclass
from datetime import datetime

from d3_mapping.resources.protos.connection.login_message_pb2 import (
    IdentificationResponse,
)
from d3_mapping.resources.protos.game.account_pb2 import AccountInformationUpdateEvent
from d3_mapping.resources.protos.game.character_management_pb2 import (
    CharacterSelectionEvent,
)
from d3_mapping.resources.protos.game.character_pb2 import (
    CharacterCharacteristicsEvent,
    CharacterLifeStatusEvent,
)
from d3_mapping.resources.protos.game.fight_pb2 import FightRefreshCharacterStatsEvent
from d3_mapping.resources.protos.game.gamemap_pb2 import (
    FightMapInformationEvent,
    MapComplementaryInformationEvent,
)
from d3_mapping.resources.protos.game.job_pb2 import JobExperiencesUpdateEvent
from d3_mapping.resources.protos.game.teleportation_pb2 import ZaapKnownListEvent

from src.core.frames.frame import Frame


@dataclass
class PlayerFrame(Frame):
    def __post_init__(self):
        self.game_info_signals.disconnected.connect(self.game_state.player.clear_state)
        self.event_manager.on(
            JobExperiencesUpdateEvent,
            self.on_job_experiences_update_event,
            originator=self,
        )
        self.event_manager.on(
            CharacterSelectionEvent,
            self.on_character_selection_event,
            originator=self,
        )
        self.event_manager.on(
            CharacterCharacteristicsEvent,
            self.on_character_characteristics_event,
            originator=self,
        )
        self.event_manager.on(
            IdentificationResponse,
            self.on_identification_response,
            originator=self,
        )
        self.event_manager.on(
            AccountInformationUpdateEvent,
            self.on_account_information_update_event,
            originator=self,
        )
        self.event_manager.on(
            FightRefreshCharacterStatsEvent,
            self.on_fight_refresh_character_stats_event,
            originator=self,
        )
        self.event_manager.on(
            ZaapKnownListEvent, self.on_zaap_known_list_event, originator=self
        )
        self.event_manager.on(
            CharacterLifeStatusEvent,
            self.on_character_life_status_event,
            originator=self,
        )

        self.game_info_signals.connected.connect(self.on_connected)
        self.game_info_signals.disconnected.connect(self.on_disconnected)
        self.game_info_signals.is_ready_to_play.connect(
            self.game_state.player.is_ready_to_play_event.set
        )

    def on_connected(self):
        def on_map_init_after_connected():
            self.game_info_signals.is_ready_to_play.emit()
            self.event_manager.clear_listener_by_origin_and_type(
                MapComplementaryInformationEvent, self
            )
            self.event_manager.clear_listener_by_origin_and_type(
                FightMapInformationEvent, self
            )

        self.event_manager.on(
            MapComplementaryInformationEvent,
            lambda _: on_map_init_after_connected(),
            originator=self,
            once=True,
        )
        self.event_manager.on(
            FightMapInformationEvent,
            lambda _: on_map_init_after_connected(),
            originator=self,
            once=True,
        )

    def on_disconnected(self):
        self.game_state.player.is_ready_to_play_event.clear()

    def on_identification_response(self, message: IdentificationResponse):
        if message.HasField("success"):
            self.game_state.player.subscription_end_date = datetime.fromisoformat(
                message.success.subscription_end_date
            )

    def on_job_experiences_update_event(self, message: JobExperiencesUpdateEvent):
        for job_xp in message.experiences:
            self.game_state.player.jobs_lvl_by_id[job_xp.job_id] = job_xp.job_level

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
                    self.game_state.player.breed_id = message.success.character.character_basic_information.character_look.breed_id
            elif message.success.character.HasField("character_remodeling_information"):
                self.game_state.player.breed_id = (
                    message.success.character.character_remodeling_information.breed_id
                )

    def on_character_characteristics_event(
        self, message: CharacterCharacteristicsEvent
    ):
        for stat in message.stats.characteristics:
            self.game_state.player.characteristic_by_id[stat.characteristic_id] = stat

    def on_account_information_update_event(self, msg: AccountInformationUpdateEvent):
        self.game_state.player.subscription_end_date = datetime.fromtimestamp(
            msg.subscription_end_date / 1000
        )

    def on_fight_refresh_character_stats_event(
        self, msg: FightRefreshCharacterStatsEvent
    ):
        if self.game_state.player.character_id != msg.fighter_id:
            return
        for characteristic in msg.stats.characteristics:
            self.game_state.player.characteristic_by_id[
                characteristic.characteristic_id
            ] = characteristic

    def on_zaap_known_list_event(self, msg: ZaapKnownListEvent):
        self.game_state.player.waypoint_map_ids = list(msg.destinations)

    def on_character_life_status_event(self, msg: CharacterLifeStatusEvent):
        self.game_state.player.life_state = msg.state
