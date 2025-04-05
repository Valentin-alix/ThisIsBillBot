from dataclasses import dataclass

from datas.protos.non_obf.game.character_pb2 import CharacterCharacteristicsEvent
from datas.protos.non_obf.game.fight_pb2 import (
    FightRefreshCharacterStatsEvent,
    FightTurnEvent,
    FightTurnFinishRequest,
)
from datas.protos.non_obf.game.fight_preparation_pb2 import (
    FightPlacementPossiblePositionsEvent,
)
from datas.protos.non_obf.game.game_action_pb2 import (
    GameActionFightCastRequest,
    GameActionFightEvent,
)
from datas.protos.non_obf.game.gamemap_pb2 import (
    FightMapInformationEvent,
    MapComplementaryInformationEvent,
)
from datas.protos.non_obf.game.spell_pb2 import (
    SpellsEvent,
)

from src.controller.forbidden_monster_controller import ForbiddenMonsterController
from src.core.frames.frame import Frame


@dataclass
class FightFrame(Frame):
    def __post_init__(self):
        self.event_manager.on(
            FightPlacementPossiblePositionsEvent,
            self.on_fight_placement_position_request,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            SpellsEvent,
            self.on_spells_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            GameActionFightCastRequest,
            self.on_game_action_fight_cast_request,
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
            FightTurnFinishRequest,
            self.before_fight_turn_finish_request,
            originator=self,
        )
        self.event_manager.on(
            GameActionFightEvent,
            self.on_game_action_fight_event,
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
            FightMapInformationEvent,
            self.on_fight_map_information_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            FightTurnEvent,
            self.on_fight_turn_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            MapComplementaryInformationEvent,
            self.on_map_complementary_information_event,
            originator=self,
            priority=self.priority,
        )

    def on_fight_placement_position_request(
        self, msg: FightPlacementPossiblePositionsEvent
    ):
        if (
            self.game_state.map.map_point.cell_id
            in msg.starting_positions.challengers_positions
        ):
            self.game_state.fight.fight_placement_possible_positions = list(
                msg.starting_positions.challengers_positions
            )
        else:
            self.game_state.fight.fight_placement_possible_positions = list(
                msg.starting_positions.defenders_positions
            )

    def on_spells_event(self, message: SpellsEvent):
        self.game_state.fight.spells = list(message.human_spells)

    def on_game_action_fight_cast_request(self, message: GameActionFightCastRequest):
        self.game_state.fight.count_casted_by_spell_id_on_current_turn[
            message.spell_id
        ] = (
            self.game_state.fight.count_casted_by_spell_id_on_current_turn.get(
                message.spell_id, 0
            )
            + 1
        )

    def on_character_characteristics_event(
        self, message: CharacterCharacteristicsEvent
    ):
        self.game_state.fight.modifier_by_type_and_spell_id.clear()
        for spell_modifier in message.stats.spell_modifiers:
            self.game_state.fight.modifier_by_type_and_spell_id[
                (spell_modifier.spell_id, spell_modifier.modifier_type)
            ] = spell_modifier

        for stat in message.stats.characteristics:
            self.game_state.fight.update_characteristic(stat)
        self.game_state.fight.sync_life_points_from_characteristics()

    def before_fight_turn_finish_request(
        self, msg: FightTurnFinishRequest
    ) -> FightTurnFinishRequest | None:
        if self.is_playing_event.is_set() and msg.is_active:
            return None
        return msg

    def on_game_action_fight_event(self, msg: GameActionFightEvent):
        if msg.HasField("death") and (
            msg.death.target_id == self.game_state.player.character_id
        ):
            self.game_state.fight.life_point = 0

        if msg.HasField("life_points_gain"):
            if msg.life_points_gain.target_id == self.game_state.player.character_id:
                self.game_state.fight.life_point += msg.life_points_gain.delta
            else:
                self.game_state.entity.actor_fight_by_id[
                    msg.life_points_gain.target_id
                ].life_point += msg.life_points_gain.delta

        if msg.HasField("life_points_lost"):
            if msg.life_points_lost.target_id == self.game_state.player.character_id:
                self.game_state.fight.life_point -= msg.life_points_lost.loss
            else:
                self.game_state.entity.actor_fight_by_id[
                    msg.life_points_lost.target_id
                ].life_point -= msg.life_points_lost.loss

    def on_fight_refresh_character_stats_event(
        self, msg: FightRefreshCharacterStatsEvent
    ):
        if self.game_state.player.character_id != msg.fighter_id:
            return
        for characteristic in msg.stats.characteristics:
            self.game_state.fight.update_characteristic(characteristic)
        self.game_state.fight.sync_life_points_from_characteristics()

    def on_fight_map_information_event(self, msg: FightMapInformationEvent):
        self.game_state.fight.count_casted_by_spell_id_on_current_turn.clear()
        self.game_state.fight.modifier_by_type_and_spell_id.clear()
        self.game_state.fight.in_fight = True

    def on_fight_turn_event(self, msg: FightTurnEvent):
        self.game_state.fight.fight_placement_possible_positions.clear()
        if msg.character_id == self.game_state.player.character_id:
            self.game_state.fight.count_casted_by_spell_id_on_current_turn.clear()
            self.game_state.fight.is_our_turn = True
            self.game_state.fight.fight_turn += 1
        else:
            self.game_state.fight.count_casted_by_spell_id_on_current_turn.clear()
            self.game_state.fight.is_our_turn = False

    def on_map_complementary_information_event(
        self, msg: MapComplementaryInformationEvent
    ):
        self.game_state.fight.modifier_by_type_and_spell_id.clear()
        self.game_state.fight.count_casted_by_spell_id_on_current_turn.clear()
        self.game_state.fight.in_fight = False
        self.game_state.fight.fight_turn = 0
        self.game_state.fight.is_our_turn = False
        self.game_state.fight.fight_placement_possible_positions.clear()

        last_atk_info = self.game_state.fight.last_atk_info
        if last_atk_info:
            unique_name_id = ForbiddenMonsterController().get_unique_name_id_from_group(
                last_atk_info.monster_group_info
            )
            if not unique_name_id:
                return
            self.logger.info(
                f"Unique monster group name_id attacked : {unique_name_id}"
            )
            if last_atk_info.from_map_id == msg.map_id:
                ForbiddenMonsterController().reset_defeat_count(
                    unique_name_id, self.logger
                )
            else:
                ForbiddenMonsterController().increment_defeat_count(
                    unique_name_id, self.logger
                )

        self.game_state.fight.last_atk_info = None
