from dataclasses import dataclass
from datetime import datetime

from protos.connection.login_message_pb2 import IdentificationResponse
from protos.game.account_pb2 import AccountInformationUpdateEvent
from protos.game.character_management_pb2 import (
    CharacterSelectionEvent,
)
from protos.game.character_pb2 import (
    CharacterCharacteristicsEvent,
    CharacterLifeStatusEvent,
    UpdateLifePointsEvent,
)
from protos.game.fight_pb2 import FightRefreshCharacterStatsEvent
from protos.game.game_action_pb2 import GameActionFightEvent
from protos.game.guild_member_pb2 import GuildMembershipEvent
from protos.game.job_pb2 import JobExperiencesUpdateEvent
from protos.game.server_pb2 import ServerSettingsEvent
from protos.game.teleportation_pb2 import ZaapKnownListEvent
from src.core.frames.frame import Frame
from src.signals.player_signals import GameInfoSignals


@dataclass
class PlayerFrame(Frame):
    game_info_signals: GameInfoSignals

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
        self.event_manager.on(
            UpdateLifePointsEvent, self.on_update_life_points_event, originator=self
        )
        self.event_manager.on(
            GameActionFightEvent, self.on_game_action_fight_event, originator=self
        )
        self.event_manager.on(
            GuildMembershipEvent, self.on_guild_member_ship_event, originator=self
        )

    def on_update_life_points_event(self, msg: UpdateLifePointsEvent):
        self.game_state.player.life_point = msg.life_points
        self.game_state.player.max_life_point = msg.max_life_points

    def on_game_action_fight_event(self, msg: GameActionFightEvent):
        if (
            msg.HasField("life_points_gain")
            and msg.life_points_gain.target_id == self.game_state.player.character_id
        ):
            self.game_state.player.life_point += msg.life_points_gain.delta
        if (
            msg.HasField("life_points_lost")
            and msg.life_points_lost.target_id == self.game_state.player.character_id
        ):
            self.game_state.player.life_point -= msg.life_points_lost.loss

    def on_identification_response(self, message: IdentificationResponse):
        if message.HasField("success"):
            self.game_state.player.subscription_end_date = datetime.fromisoformat(
                message.success.subscription_end_date
            )

    def on_server_settings_event(self, message: ServerSettingsEvent):
        self.game_state.player.game_type = message.game_type

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
                    self.game_state.player.breed_id = (
                        message.success.character.character_basic_information.character_look.breed_id
                    )
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

    def on_guild_member_ship_event(self, msg: GuildMembershipEvent):
        self.game_state.player.guild_information = msg.guild_information
        self.game_state.player.guild_rank_id = msg.rank_id


if __name__ == "__main__":
    temp = datetime.fromtimestamp(1734209975000 / 1000)
    print(temp)
