from dataclasses import dataclass

from datas.protos.non_obf.game.character_pb2 import CharacterCharacteristicsEvent
from datas.protos.non_obf.game.common_pb2 import (
    FightInvisibilityState,
    FightRemovableEffect,
)
from datas.protos.non_obf.game.context_pb2 import ContextCreationEvent
from datas.protos.non_obf.game.fight_pb2 import (
    FightRefreshCharacterStatsEvent,
    FightSynchronizeEvent,
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
from dofus_unity_reader.game_constants.characteristic import CharacteristicEnum

from src.controller.game_data import GameDataController
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
            FightSynchronizeEvent,
            self.on_fight_synchronize_event,
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
        self.event_manager.on(
            ContextCreationEvent,
            self.on_context_creation_event,
            originator=self,
            priority=self.priority,
        )

    def on_context_creation_event(self, msg: ContextCreationEvent):
        self.game_state.fight.in_fight = (
            msg.context == ContextCreationEvent.GameContext.FIGHT
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
        self.game_state.fight.last_cast_turn_by_spell_id[message.spell_id] = (
            self.game_state.fight.fight_turn
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
        hp_before = self.game_state.fight.life_point
        self.game_state.fight.sync_life_points_from_characteristics()
        self._log_life_resync("CharacterCharacteristicsEvent", hp_before)

    def before_fight_turn_finish_request(
        self, msg: FightTurnFinishRequest
    ) -> FightTurnFinishRequest | None:
        if self.is_playing_event.is_set():
            return None
        return msg

    def on_game_action_fight_event(self, msg: GameActionFightEvent):
        if msg.HasField("death") and (
            msg.death.target_id == self.game_state.player.character_id
        ):
            hp_before = self.game_state.fight.life_point
            self.logger.info(
                "Player HP death event: "
                f"hp_before={hp_before}, source_id={msg.source_id}, "
                f"death_source_id={msg.death.source_id}, target_id={msg.death.target_id}"
            )
            self.game_state.fight.life_point = 0
            self.logger.info("Player HP death applied: hp_after=0")

        if msg.HasField("life_points_gain"):
            if msg.life_points_gain.target_id == self.game_state.player.character_id:
                hp_before = self.game_state.fight.life_point
                hp_after = hp_before + msg.life_points_gain.delta
                self.logger.info(
                    "Player HP gain event: "
                    f"hp_before={hp_before}, delta={msg.life_points_gain.delta}, "
                    f"hp_after={hp_after}, source_id={msg.source_id}, "
                    f"target_id={msg.life_points_gain.target_id}"
                )
                self.game_state.fight.life_point = hp_after
            else:
                if (
                    msg.life_points_gain.target_id
                    not in self.game_state.entity.actor_fight_by_id
                ):
                    self.logger.error(
                        "Non-player HP gain targets missing fight actor: "
                        f"target_id={msg.life_points_gain.target_id}, "
                        f"delta={msg.life_points_gain.delta}, source_id={msg.source_id}"
                    )
                self.game_state.entity.actor_fight_by_id[
                    msg.life_points_gain.target_id
                ].life_point += msg.life_points_gain.delta

        if msg.HasField("life_points_lost"):
            if msg.life_points_lost.target_id == self.game_state.player.character_id:
                hp_before = self.game_state.fight.life_point
                hp_after = max(hp_before - msg.life_points_lost.loss, 0)
                log_message = (
                    "Player HP loss event: "
                    f"hp_before={hp_before}, loss={msg.life_points_lost.loss}, "
                    f"shield_loss={msg.life_points_lost.shield_loss}, "
                    f"permanent_damages={msg.life_points_lost.permanent_damages}, "
                    f"element_id={msg.life_points_lost.element_id}, "
                    f"hp_after={hp_after}, source_id={msg.source_id}, "
                    f"target_id={msg.life_points_lost.target_id}"
                )
                if msg.life_points_lost.loss > hp_before:
                    self.logger.info(f"{log_message} (fatal damage clamped to 0 HP)")
                else:
                    self.logger.info(log_message)
                self.game_state.fight.life_point = hp_after
            else:
                if (
                    msg.life_points_lost.target_id
                    not in self.game_state.entity.actor_fight_by_id
                ):
                    self.logger.error(
                        "Non-player HP loss targets missing fight actor: "
                        f"target_id={msg.life_points_lost.target_id}, "
                        f"loss={msg.life_points_lost.loss}, source_id={msg.source_id}"
                    )
                actor_fight = self.game_state.entity.actor_fight_by_id[
                    msg.life_points_lost.target_id
                ]
                actor_fight.life_point = max(
                    actor_fight.life_point - msg.life_points_lost.loss,
                    0,
                )

        # Effects/invisibility are tracked only for non-player fighters (the player
        # is kept out of actor_fight_by_id, its state lives in game_state.fight).
        player_id = self.game_state.player.character_id

        if (
            msg.HasField("removable_effect")
            and msg.removable_effect.effect.target_id != player_id
        ):
            self._handle_removable_effect(msg.removable_effect.effect)

        if msg.HasField("spell_remove") and msg.spell_remove.target_id != player_id:
            self.game_state.entity.remove_fight_actor_effect(
                msg.spell_remove.target_id, msg.spell_remove.effect_remove.effect
            )

        if msg.HasField("invisibility") and msg.invisibility.target_id != player_id:
            self.game_state.entity.set_fight_actor_invisibility(
                msg.invisibility.target_id, msg.invisibility.invisibility_state
            )

        if (
            msg.HasField("invisible_detected")
            and msg.invisible_detected.target_id != player_id
        ):
            self.game_state.entity.set_fight_actor_invisibility(
                msg.invisible_detected.target_id, FightInvisibilityState.DETECTED
            )

    def _handle_removable_effect(self, effect: FightRemovableEffect) -> None:
        # Only track state-carrying effects; pure stat boosts (state_id 0) are ignored.
        state_id = effect.temporary_boost_effect.state_id
        if (
            effect.dissipation_state == FightRemovableEffect.REALLY_NOT_DISSIPATED
            and state_id
        ):
            self.game_state.entity.set_fight_actor_effect(
                effect.target_id, effect.uid, state_id
            )
        else:
            self.game_state.entity.remove_fight_actor_effect(
                effect.target_id, effect.uid
            )

    def on_fight_synchronize_event(self, msg: FightSynchronizeEvent):
        player_id = self.game_state.player.character_id
        player_fighter = next(
            actor for actor in msg.fighters if actor.actor_id == player_id
        )
        for (
            characteristic
        ) in player_fighter.actor_information.fighter.stats.characteristics:
            self.game_state.fight.update_characteristic(characteristic)
        hp_before = self.game_state.fight.life_point
        self.game_state.fight.sync_life_points_from_characteristics()
        self._log_life_resync("FightSynchronizeEvent", hp_before)

    def on_fight_refresh_character_stats_event(
        self, msg: FightRefreshCharacterStatsEvent
    ):
        if self.game_state.player.character_id != msg.fighter_id:
            return
        has_life_stat = False
        for characteristic in msg.stats.characteristics:
            self.game_state.fight.update_characteristic(characteristic)
            if characteristic.characteristic_id in _LIFE_CHARACTERISTIC_IDS:
                has_life_stat = True
        if not has_life_stat:
            return
        hp_before = self.game_state.fight.life_point
        self.game_state.fight.sync_life_points_from_characteristics()
        self._log_life_resync("FightRefreshCharacterStatsEvent", hp_before)

    def _log_life_resync(self, source_event: str, hp_before: int) -> None:
        life_points = self.game_state.fight.get_stat_by_id(
            CharacteristicEnum.LIFE_POINTS
        )
        vitality = self.game_state.fight.get_stat_by_id(CharacteristicEnum.VITALITY)
        current_life_delta = self.game_state.fight.get_stat_by_id(
            CharacteristicEnum.CUR_LIFE
        )
        self.logger.info(
            "Player HP resync: "
            f"source={source_event}, hp_before={hp_before}, "
            f"life_points={life_points}, vitality={vitality}, "
            f"cur_life={current_life_delta}, "
            f"hp_after={self.game_state.fight.life_point}, "
            f"max_hp_after={self.game_state.fight.max_life_point}"
        )

    def on_fight_map_information_event(self, msg: FightMapInformationEvent):
        self.game_state.fight.count_casted_by_spell_id_on_current_turn.clear()
        self.game_state.fight.last_cast_turn_by_spell_id.clear()
        self.game_state.fight.modifier_by_type_and_spell_id.clear()
        self.game_state.fight.in_fight = True
        self.logger.debug("Fight start: cleared per-fight cooldown/cast tracking")

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
            unique_name_id = GameDataController().get_unique_name_id_from_group(
                last_atk_info.monster_group_info
            )
            if not unique_name_id:
                return
            self.logger.info(
                f"Unique monster group name_id attacked : {unique_name_id}"
            )
            if last_atk_info.from_map_id == msg.map_id:
                GameDataController().reset_defeat_count(unique_name_id, self.logger)
            else:
                GameDataController().increment_defeat_count(unique_name_id, self.logger)

        self.game_state.fight.last_atk_info = None


_LIFE_CHARACTERISTIC_IDS = {
    CharacteristicEnum.LIFE_POINTS,
    CharacteristicEnum.VITALITY,
    CharacteristicEnum.CUR_LIFE,
}
