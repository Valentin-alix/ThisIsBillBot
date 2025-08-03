from collections.abc import Callable
from dataclasses import dataclass, field

from datas.protos.non_obf.game.common_pb2 import (
    CharacterCharacteristic,
    CharacterCharacteristicDetailed,
)
from datas.protos.non_obf.game.fight_pb2 import (
    FightTurnEvent,
    FightTurnFinishRequest,
)
from datas.protos.non_obf.game.game_action_pb2 import GameActionFightEvent
from dofus_unity_reader.game_constants.characteristic import CharacteristicEnum
from dofus_unity_reader.grid.map_point import MapPoint
from dofus_unity_reader.models.datas.spell_levels_root import SpellLevelsRootItem

from src.core.behaviors.behavior import Behavior
from src.core.behaviors.farms.fight.fight_movement_behavior import FightMovementBehavior
from src.core.behaviors.farms.fight.fight_spell_behavior import FightSpellBehavior
from src.core.behaviors.movements.map_move_behavior import MapMoveError
from src.core.engine.contexts import AttackContext
from src.core.engine.fights.attack.attacker import Attacker
from src.core.engine.fights.attack.buff import find_best_self_buff
from src.core.engine.fights.attack.heal import find_best_self_heal
from src.core.engine.movements.map.path_finding.path_finding import Pathfinding
from src.services.human_timings import HumanTimingsService

DO_RUNAWAY_AFTER_ATK = True


@dataclass
class FightTurnBehavior(Behavior):
    fight_movement_behavior: FightMovementBehavior
    path_finding: Pathfinding
    fight_spell_behavior: FightSpellBehavior
    attacker: Attacker

    did_attack: bool = field(init=False, default=False)
    did_cast_support_spell: bool = field(init=False, default=False)
    last_cast_spell_id: int | None = field(init=False, default=None)

    def run(self) -> None:
        self.did_attack = False
        self.did_cast_support_spell = False
        self.last_cast_spell_id = None
        self.event_manager.on(FightTurnEvent, lambda _: self.finish(), originator=self)
        self.event_manager.on(
            GameActionFightEvent,
            self.on_game_action_fight_event,
            originator=self,
        )
        context = self._get_attack_context_or_finish()
        if context is None:
            return
        self.logger.info(
            f"Turn {context.fight_turn}: HP {context.life_point}/{context.max_life_point}, "
            f"AP {context.action_points}, MP {context.movement_points}, "
            f"{len(context.enemy_actors)} enemies"
        )
        self.try_primary_attack_or_continue()

    def _get_attack_context_or_finish(self) -> AttackContext | None:
        context = self.game_state.get_attack_context_if_available()
        if context is not None:
            return context
        if self.game_state.fight.life_point <= 0:
            self.finish(MapMoveError.PLAYER_DEAD)
        else:
            self.finish()
        return None

    def on_game_action_fight_event(self, msg: GameActionFightEvent) -> None:
        if msg.HasField("death") and (msg.death.target_id == self.game_state.player.character_id):
            self.finish(MapMoveError.PLAYER_DEAD)

    def _cast_self_spell(
        self,
        spell_lvl: SpellLevelsRootItem,
        target_mp: MapPoint,
        on_done: Callable[[], None],
    ) -> None:
        """Cast a self-targeted spell, then run ``on_done`` (re-entrant step)."""

        def on_finished(error_code: str | None) -> None:
            self.raise_if_error(error_code)
            self.did_cast_support_spell = True
            on_done()

        self._schedule_spell_cast(spell_lvl.spellId, target_mp, on_finished)

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

        self.run_timer(
            HumanTimingsService().get_timing_fight_action(same_spell),
            start_spell,
        )

    def try_primary_attack_or_continue(self) -> None:
        context = self._get_attack_context_or_finish()
        if context is None:
            return
        attack_info = self.attacker.find_best_attack_from_mp(
            context,
            allowed_elements=frozenset({*context.primary_and_second_elem}),
        )
        if attack_info is None:
            return self.try_self_heal_or_continue()
        self._do_attack(attack_info, self.try_primary_attack_or_continue)

    def try_self_heal_or_continue(self) -> None:
        context = self._get_attack_context_or_finish()
        if context is None:
            return
        heal_spell = find_best_self_heal(context, self.logger)
        if heal_spell is None:
            return self.try_self_buff_or_continue()
        self._cast_self_spell(
            heal_spell,
            context.player_map_point,
            self.try_self_heal_or_continue,
        )

    def try_self_buff_or_continue(self) -> None:
        """Cast beneficial self-buffs (once each per fight) before secondary attacks.

        Buffs boost the damage of every subsequent cast this turn. Re-entered after
        each buff; terminates once all buffs are used or AP/cast limits are reached.
        """
        context = self._get_attack_context_or_finish()
        if context is None:
            return
        buff_spell = find_best_self_buff(context, self.logger)
        if buff_spell is None:
            return self.find_and_do_attack()
        self._cast_self_spell(buff_spell, context.player_map_point, self.try_self_buff_or_continue)

    def find_and_do_attack(self) -> None:
        context = self._get_attack_context_or_finish()
        if context is None:
            return
        if not context.enemy_actors:
            self.logger.info("No enemies left, passing turn")
            return self.pass_turn()

        attack_info = self.attacker.find_best_attack_from_mp(context)
        if attack_info is None:
            self.logger.info("Attack not found")
            if DO_RUNAWAY_AFTER_ATK and self.did_attack:
                self.logger.info("Go go run away")
                run_away = True
            else:
                run_away = False

            def on_movement_finished(error_code: str | None) -> None:
                self.on_fight_movement_behavior_finished(
                    error_code,
                    callback=lambda: self.run_timer(
                        HumanTimingsService().get_timing_before_pass_turn(),
                        self.pass_turn,
                    ),
                )

            return self.fight_movement_behavior.start(
                callback=on_movement_finished,
                parent=self,
                run_away=run_away,
            )

        self._do_attack(attack_info, self.find_and_do_attack)

    def _do_attack(
        self,
        attack_info: tuple[MapPoint, SpellLevelsRootItem, MapPoint],
        on_replan: Callable[[], None],
    ) -> None:
        self.did_attack = True
        move_mp, spell_lvl, attack_mp = attack_info

        position_before_move = self.game_state.map.map_point
        move_path = self.path_finding.find_path(
            self.game_state.get_map_movement_context(),
            position_before_move,
            {move_mp},
            allow_diag=False,
            allow_trough_entity=False,
        )

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

        def on_attack_movement_finished(error_code: str | None) -> None:
            self.on_fight_movement_behavior_finished(
                error_code,
                callback=cast_attack,
            )

        self.fight_movement_behavior.start(
            callback=on_attack_movement_finished,
            parent=self,
            move_path=move_path,
        )

    def on_fight_movement_behavior_finished(
        self, error_code: str | None, callback: Callable[[], None]
    ) -> None:
        if error_code is MapMoveError.PLAYER_DEAD:
            return self.finish(error_code)
        if error_code is MapMoveError.CANCELED_MOVEMENT:
            return self.find_and_do_attack()
        if error_code is MapMoveError.REFUSED:
            self.game_state.fight.update_characteristic(
                CharacterCharacteristic(
                    characteristic_id=CharacteristicEnum.MOVEMENT_POINTS,
                    detailed=CharacterCharacteristicDetailed(
                        base=6,
                        additional=0,
                        objects_and_mount_bonus=0,
                        alignment_gift_bonus=0,
                        context_modification=-6,
                        temporary=0,
                    ),
                )
            )
            return self.find_and_do_attack()
        elif error_code is MapMoveError.CELL_TAKEN:
            # cell is probably taken by invisible enemy
            return self.pass_turn()
        elif error_code is not None:
            return self.pass_turn()
        callback()

    def on_fight_spell_behavior_finished(self, error_code: str | None) -> None:
        self.raise_if_error(error_code)
        self.try_primary_attack_or_continue()

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
