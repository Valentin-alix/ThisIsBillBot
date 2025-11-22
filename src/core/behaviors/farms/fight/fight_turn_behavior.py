from collections.abc import Callable
from dataclasses import dataclass, field, replace

from DBDofusUnity.datas.protos.non_obf.game.fight_pb2 import (
    FightTurnEvent,
    FightTurnFinishRequest,
)
from DBDofusUnity.dofus_unity_reader.grid.map_point import MapPoint
from DBDofusUnity.dofus_unity_reader.models.datas.spell_levels_root import SpellLevelsRootItem
from src.core.behaviors.farms.fight.fight_listener_behavior import FightListenerBehavior
from src.core.behaviors.farms.fight.fight_movement_behavior import FightMovementBehavior
from src.core.behaviors.farms.fight.fight_spell_behavior import FightSpellBehavior
from src.core.behaviors.movements.map_move_behavior import MapMoveError
from src.core.engine.contexts import AttackContext
from src.core.engine.fights.attack.attacker import Attacker
from src.core.engine.fights.attack.breed_abilities import BreedAbilitySelector
from src.services.human_timings import HumanTimingsService


@dataclass
class FightTurnBehavior(FightListenerBehavior):
    fight_movement_behavior: FightMovementBehavior
    fight_spell_behavior: FightSpellBehavior
    attack_selector: Attacker
    breed_ability_selector: BreedAbilitySelector

    did_attack: bool = field(init=False, default=False)
    did_cast_support_spell: bool = field(init=False, default=False)
    last_cast_spell_id: int | None = field(init=False, default=None)

    def run(self) -> None:
        self.did_attack = False
        self.did_cast_support_spell = False
        self.last_cast_spell_id = None
        self.event_manager.on(FightTurnEvent, lambda _: self.finish(), originator=self)
        self.register_fight_death_check()
        context = self._get_attack_context_or_finish()
        if context is None:
            return
        self.logger.info(
            f"Turn {context.fight_turn}: HP {context.life_point}/{context.max_life_point}, "
            f"AP {context.action_points}, MP {context.movement_points}, "
            f"{len(context.enemy_actors)} enemies"
        )
        self._advance_turn()

    def _get_attack_context_or_finish(self) -> AttackContext | None:
        context = self.game_state.get_attack_context_if_available()
        if context is not None:
            return context
        if self.game_state.fight.life_point <= 0:
            self.finish(MapMoveError.PLAYER_DEAD)
        else:
            self.finish()
        return None

    def _cast_self_spell(
        self,
        context: AttackContext,
        spell_lvl: SpellLevelsRootItem,
        on_done: Callable[[], None],
    ) -> None:
        def on_finished(error_code: str | None) -> None:
            self.raise_if_error(error_code)
            self.did_cast_support_spell = True
            on_done()

        self._schedule_spell_cast(spell_lvl.spellId, context.player_map_point, on_finished)

    def _schedule_spell_cast(
        self,
        spell_id: int,
        target_mp: MapPoint,
        callback: Callable[[str | None], None],
    ) -> None:
        same_spell = spell_id == self.last_cast_spell_id

        def start_spell() -> None:
            self.last_cast_spell_id = spell_id
            self.fight_spell_behavior.start(
                spell_id=spell_id, target_mp=target_mp, parent=self, callback=callback
            )

        self.run_timer(HumanTimingsService().get_timing_fight_action(same_spell), start_spell)

    def _attack_context_with_reserved_ap(self, context: AttackContext) -> AttackContext:
        """Cap the AP the attack search may spend, holding back a pending support action's AP."""
        reserved_ap = self.breed_ability_selector.get_reserved_ap(context)
        if reserved_ap <= 0:
            return context
        return replace(context, action_points=max(context.action_points - reserved_ap, 0))

    def _advance_turn(self, stage: int = 0) -> None:
        """One-way waterfall (urgent breed action, primary attack, heal, buff): each
        stage retries itself until it finds nothing, then falls through and never
        re-checks."""
        context = self._get_attack_context_or_finish()
        if context is None:
            return

        if stage <= 0:
            urgent_action = self.breed_ability_selector.find_urgent_support_action(
                self._attack_context_with_reserved_ap(context)
            )
            if urgent_action is not None:
                _, urgent_spell_lvl, _ = urgent_action
                return self._cast_self_spell(context, urgent_spell_lvl, lambda: self._advance_turn(1))
            stage = 1

        if stage <= 1:
            primary_attack_info = self.attack_selector.find_best_attack_from_mp(
                self._attack_context_with_reserved_ap(context),
                allowed_elements=frozenset({*context.primary_and_second_elem}),
            )
            if primary_attack_info is not None:
                return self._do_move_then_attack(primary_attack_info, lambda: self._advance_turn(1))
            stage = 2

        if stage <= 2:
            heal_spell = self.attack_selector.find_best_self_heal(
                self._attack_context_with_reserved_ap(context)
            )
            if heal_spell is not None:
                return self._cast_self_spell(context, heal_spell, lambda: self._advance_turn(2))
            stage = 3

        if stage <= 3:
            buff_spell = self.attack_selector.find_best_self_buff(
                self._attack_context_with_reserved_ap(context)
            )
            if buff_spell is not None:
                return self._cast_self_spell(context, buff_spell, lambda: self._advance_turn(3))

        self._find_move_attack(context)

    def _find_move_attack(self, context: AttackContext) -> None:
        if not context.enemy_actors:
            self.logger.info("No enemies left, passing turn")
            return self.pass_turn()

        attack_info = self.attack_selector.find_best_attack_from_mp(
            self._attack_context_with_reserved_ap(context)
        )
        if attack_info is None:
            support_action = self.breed_ability_selector.find_support_action(context)
            if support_action is not None:
                return self._do_move_then_attack(support_action, self._retry_find_and_do_attack)

            attack_info = self.attack_selector.find_best_attack_from_mp(context)

        if attack_info is not None:
            return self._do_move_then_attack(attack_info, self._retry_find_and_do_attack)

        self.logger.info("Attack not found")

        def on_movement_finished(error_code: str | None, cell_mp: MapPoint | None = None) -> None:
            self.on_fight_movement_behavior_finished(
                error_code,
                cell_mp,
                callback=lambda: self.run_timer(
                    HumanTimingsService().get_timing_before_pass_turn(), self.pass_turn
                ),
            )

        return self.fight_movement_behavior.start(callback=on_movement_finished, parent=self)

    def _do_move_then_attack(
        self,
        attack_info: tuple[MapPoint, SpellLevelsRootItem, MapPoint],
        on_replan: Callable[[], None],
    ) -> None:
        self.did_attack = True
        move_mp, spell_lvl, attack_mp = attack_info

        position_before_move = self.game_state.map.map_point
        move_path = self.fight_movement_behavior.find_path_to_cell(move_mp)

        def cast_attack() -> None:
            current_mp = self.game_state.map.map_point
            if current_mp != move_mp:
                if current_mp != position_before_move:
                    self.logger.info(
                        f"Did not reach planned cast cell {move_mp} (now at {current_mp}), re-planning attack"
                    )
                    return on_replan()
                self.logger.info(f"Could not reach planned cast cell {move_mp}, passing turn")
                return self.pass_turn()

            self._schedule_spell_cast(
                spell_lvl.spellId,
                attack_mp,
                self.on_fight_spell_behavior_finished,
            )

        def on_attack_movement_finished(error_code: str | None, cell_mp: MapPoint | None = None) -> None:
            self.on_fight_movement_behavior_finished(
                error_code,
                cell_mp,
                callback=cast_attack,
            )

        self.fight_movement_behavior.start(
            callback=on_attack_movement_finished, parent=self, move_path=move_path
        )

    def on_fight_movement_behavior_finished(
        self,
        error_code: str | None,
        cell_mp: MapPoint | None,
        callback: Callable[[], None],
    ) -> None:
        if error_code is MapMoveError.PLAYER_DEAD:
            return self.finish(error_code)
        if error_code is MapMoveError.CANCELED_MOVEMENT:
            return self._retry_find_and_do_attack()
        elif error_code is MapMoveError.CELL_TAKEN:
            assert cell_mp
            self.logger.info(f"Cell {cell_mp.cell_id} taken (likely invisible enemy), blocking it")
            self.game_state.fight.add_invisible_enemy_cell(cell_mp.cell_id)
            return self._retry_find_and_do_attack()
        elif error_code is not None:
            self.logger.error(f"Unexpected map move error during fight turn: {error_code}")
            return self.pass_turn()
        callback()

    def _retry_find_and_do_attack(self) -> None:
        context = self._get_attack_context_or_finish()
        if context is None:
            return
        self._find_move_attack(context)

    def on_fight_spell_behavior_finished(self, error_code: str | None) -> None:
        self.raise_if_error(error_code)
        self._advance_turn()

    def pass_turn(self) -> None:
        context = self.game_state.get_attack_context_if_available()
        if context is not None:
            message = (
                f"Passing turn: attacked={self.did_attack}, "
                f"support_cast={self.did_cast_support_spell}, "
                f"AP={context.action_points}, MP={context.movement_points}, "
                f"enemies={len(context.enemy_actors)}"
            )
            if (
                not self.did_attack
                and not self.did_cast_support_spell
                and context.action_points > 0
                and context.enemy_actors
            ):
                self.logger.warning(message)
            else:
                self.logger.info(message)
        req = FightTurnFinishRequest()
        self.event_manager.send(req)
