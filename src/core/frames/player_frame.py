import sys
from dataclasses import dataclass, field
from threading import Timer

from d3_mapping.resources.protos.connection.login_message_pb2 import (
    IdentificationResponse,
)
from d3_mapping.resources.protos.game.character_management_pb2 import (
    CharacterSelectionEvent,
)
from d3_mapping.resources.protos.game.character_pb2 import (
    CharacterCharacteristicsEvent,
    CharacterCharacteristicUpgradeRequest,
    CharacterLevelUpEvent,
    CharacterLifeStatusEvent,
    PlayerStatusUpdateRequest,
    UpdateLifePointsEvent,
)
from d3_mapping.resources.protos.game.dialog_pb2 import DialogLeaveRequest
from d3_mapping.resources.protos.game.exchange_pb2 import ExchangeMoveKamaRequest
from d3_mapping.resources.protos.game.fight_pb2 import FightRefreshCharacterStatsEvent
from d3_mapping.resources.protos.game.game_action_pb2 import GameActionFightEvent
from d3_mapping.resources.protos.game.gamemap_pb2 import (
    FightMapInformationEvent,
    MapComplementaryInformationEvent,
)
from d3_mapping.resources.protos.game.guild_member_pb2 import GuildMembershipEvent
from d3_mapping.resources.protos.game.inventory_pb2 import InventoryWeightEvent
from d3_mapping.resources.protos.game.job_pb2 import JobExperiencesUpdateEvent
from d3_mapping.resources.protos.game.teleportation_pb2 import ZaapKnownListEvent

from src.controller.scraping_d3 import ScrapingD3Controller
from src.core.frames.frame import Frame
from src.core.logic.stats.characteristic import get_max_characteristic_per_point
from src.interfaces.enums.priority import PriorityEnum


@dataclass
class PlayerFrame(Frame):
    _timer: Timer | None = field(init=False, default=None)

    def __post_init__(self):
        self.game_info_signals.disconnected.connect(self.game_state.player.clear_state)
        self.event_manager.on(
            JobExperiencesUpdateEvent,
            self.on_job_experiences_update_event,
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
            CharacterCharacteristicsEvent,
            self.on_character_characteristics_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.before(
            PlayerStatusUpdateRequest,
            self.before_player_status_update_request,
            originator=self,
        )
        self.event_manager.on(
            IdentificationResponse,
            self.on_identification_response,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            FightRefreshCharacterStatsEvent,
            self.on_fight_refresh_character_stats_event,
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
            CharacterLifeStatusEvent,
            self.on_character_life_status_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            CharacterLevelUpEvent,
            self.on_character_level_up_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            UpdateLifePointsEvent,
            self.on_update_life_points_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            GameActionFightEvent,
            self.on_game_action_fight_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            GuildMembershipEvent,
            self.on_guild_members_ship_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            InventoryWeightEvent,
            self.on_inventory_weight_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            ExchangeMoveKamaRequest,
            self.on_exchange_move_kama_request,
            originator=self,
            priority=self.priority,
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
        if message.error.ban_end_date != "":
            print(
                f"Player {self.game_state.player.character_name} has been banned rip, exiting program"
            )
            sys.exit()

    def on_job_experiences_update_event(self, message: JobExperiencesUpdateEvent):
        for job_xp in message.experiences:
            # round to ten digit lower bc only that matters
            self.game_state.player.jobs_lvl_by_id[job_xp.job_id] = max(
                (job_xp.job_level // 10) * 10, 1
            )

    def on_character_selection_event(self, message: CharacterSelectionEvent):
        if message.HasField("success"):
            self.game_state.player.character_id = message.success.character.id
            ScrapingD3Controller.create_character(
                self.game_state.player.character_id, self.game_state.player.server_id
            )
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

    def on_character_level_up_event(self, msg: CharacterLevelUpEvent):
        self.game_state.player.level = msg.new_level

        if self.is_playing_event.is_set():
            chance = get_max_characteristic_per_point(msg.new_level)
            self.logger.info(f"New amount of base chance : {chance}")
            req = CharacterCharacteristicUpgradeRequest(chance=chance)
            self.event_manager.send(req)

    def on_guild_members_ship_event(self, msg: GuildMembershipEvent):
        self.game_state.player.has_guild = True

    def on_exchange_move_kama_request(self, msg: ExchangeMoveKamaRequest):
        self.game_state.inventory.kamas += msg.quantity

    def on_inventory_weight_event(self, message: InventoryWeightEvent):
        self.game_state.inventory.inventory_weight = message.inventory_weight
        self.game_state.inventory.weight_max = message.weight_max

    def before_dialog_leave_request(self, msg: DialogLeaveRequest):
        if self.is_playing_event.is_set():
            self.logger.info("Cancel dialog leave request from client")
            return None
        return msg

    def before_player_status_update_request(self, msg: PlayerStatusUpdateRequest):
        if self.is_playing_event.is_set():
            return None
        return msg
