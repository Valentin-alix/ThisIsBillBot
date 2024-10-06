from dataclasses import dataclass
from datetime import datetime

from db_dofus_unity.protos.connection.login_message_pb2 import IdentificationResponse
from db_dofus_unity.protos.game.account_pb2 import AccountInformationUpdateEvent
from db_dofus_unity.protos.game.character_management_pb2 import (
    CharacterSelectionEvent,
)
from db_dofus_unity.protos.game.character_pb2 import CharacterCharacteristicsEvent
from db_dofus_unity.protos.game.connection_pb2 import ReloginTokenEvent
from db_dofus_unity.protos.game.fight_pb2 import FightRefreshCharacterStatsEvent
from db_dofus_unity.protos.game.job_pb2 import JobExperiencesUpdateEvent
from db_dofus_unity.protos.game.server_pb2 import ServerSettingsEvent
from db_dofus_unity.protos.game.teleportation_pb2 import ZaapKnownListEvent
from src.core.frames.frame import Frame
from src.core.states.entity_state import EntityState
from src.core.states.player_state import PlayerState
from src.signals.player_signals import GameInfoSignals


@dataclass
class PlayerFrame(Frame):
    game_info_signals: GameInfoSignals
    player_state: PlayerState
    entity_state: EntityState

    def __post_init__(self):
        self.event_manager.on(
            ServerSettingsEvent,
            self.on_server_settings_event,
            originator=self,
        )
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
            ReloginTokenEvent,
            self.on_re_login_event,
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

    def on_identification_response(self, message: IdentificationResponse):
        if message.HasField("success"):
            self.player_state.subscription_end_date = datetime.fromisoformat(
                message.success.subscription_end_date
            )

    def on_server_settings_event(self, message: ServerSettingsEvent):
        self.player_state.game_type = message.game_type

    def on_job_experiences_update_event(self, message: JobExperiencesUpdateEvent):
        self.player_state.jobs_lvl_by_id = {
            job_xp.job_id: job_xp.job_level for job_xp in message.experiences
        }

    def on_character_selection_event(self, message: CharacterSelectionEvent):
        if message.HasField("success"):
            self.player_state.character_id = message.success.character.id
            if message.success.character.HasField("character_basic_information"):
                self.player_state.level = (
                    message.success.character.character_basic_information.level
                )
                if message.success.character.character_basic_information.HasField(
                    "character_look"
                ):
                    self.player_state.breed_id = (
                        message.success.character.character_basic_information.character_look.breed_id
                    )
            elif message.success.character.HasField("character_remodeling_information"):
                self.player_state.breed_id = (
                    message.success.character.character_remodeling_information.breed_id
                )

            self.game_info_signals.connected.emit()

    def on_re_login_event(self, message: ReloginTokenEvent):
        self.player_state.character_id = 0
        self.game_info_signals.disconnected.emit()

    def on_character_characteristics_event(
        self, message: CharacterCharacteristicsEvent
    ):
        for stat in message.stats.characteristics:
            self.player_state.characteristic_by_id[stat.characteristic_id] = stat

    def on_account_information_update_event(self, msg: AccountInformationUpdateEvent):
        self.player_state.subscription_end_date = datetime.fromtimestamp(
            msg.subscription_end_date
        )

    def on_fight_refresh_character_stats_event(
        self, msg: FightRefreshCharacterStatsEvent
    ):
        if self.player_state.character_id != msg.fighter_id:
            return
        for characteristic in msg.stats.characteristics:
            self.player_state.characteristic_by_id[characteristic.characteristic_id] = (
                characteristic
            )

    def on_zaap_known_list_event(self, msg: ZaapKnownListEvent):
        self.player_state.waypoint_ids = list(msg.destinations)
