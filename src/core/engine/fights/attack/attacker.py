from collections import defaultdict
from dataclasses import dataclass
from typing import NamedTuple

from DBDofusUnity.datas.protos.non_obf.game.common_pb2 import SpellModifierType
from DBDofusUnity.dofus_unity_reader.data_center.data_reader import DataReader
from DBDofusUnity.dofus_unity_reader.data_center.i18n import I18N
from DBDofusUnity.dofus_unity_reader.game_constants.characteristic import EffectElement
from DBDofusUnity.dofus_unity_reader.game_constants.directions import DirectionsEnum
from DBDofusUnity.dofus_unity_reader.game_constants.spell_shape_enum import SpellShapeEnum
from DBDofusUnity.dofus_unity_reader.grid.map_point import MapPoint
from DBDofusUnity.dofus_unity_reader.models.datas.spell_levels_root import SpellLevelsRootItem

from src.core.engine.contexts import AttackContext, FightReachableContext
from src.core.engine.fights.attack.cast_validator import can_cast_spell_on_mp
from src.core.engine.fights.attack.models import RejectionStat
from src.core.engine.fights.attack.spell_filter import get_valid_spells_for_turn
from src.core.engine.fights.attack.weight_calculator import calculate_attack_weight
from src.core.engine.fights.damage_calculator import DamageCalculator
from src.core.engine.fights.reachable_cells.fight_reachable_cells import (
    FightReachableCells,
)
from src.core.engine.fights.spell import (
    does_spell_need_taken_cell,
    get_possible_mp_spell,
)
from src.core.engine.fights.spell_zone import get_zone_mps
from src.core.engine.movements.map.path_finding.path_finding import Pathfinding
from src.services.logging_utils.contextual_logger import ContextualLogger


class BestAttack(NamedTuple):
    total_weight: float
    remaining_pm: int
    movable_mp: MapPoint
    spell_lvl: SpellLevelsRootItem
    targetable_mp: MapPoint


class WeightCacheKey(NamedTuple):
    spell_lvl: SpellLevelsRootItem
    direction: DirectionsEnum
    targetable_mp: MapPoint


@dataclass
class Attacker(ContextualLogger):
    fight_reachable_cells: FightReachableCells
    damage_calculator: DamageCalculator
    path_finding: Pathfinding

    def find_best_attack_from_mp(
        self,
        context: AttackContext,
        *,
        allowed_elements: frozenset[EffectElement] | None = None,
    ) -> tuple[MapPoint, SpellLevelsRootItem, MapPoint] | None:
        entities_id_by_mp: dict[MapPoint, int] = {
            MapPoint.from_cell_id(actor.disposition.cell_id): actor.actor_id
            for actor in context.actor_by_id.values()
            if actor.disposition.cell_id != -1
        }
        entities_mp = set(entities_id_by_mp.keys())
        enemies = context.enemy_actors
        enemies_mp = {MapPoint.from_cell_id(enemy.disposition.cell_id) for enemy in enemies}
        enemies_data = context.enemies_data

        movable_mps = self.fight_reachable_cells.search(
            FightReachableContext(
                map_id=context.map_id,
                player_map_point=context.player_map_point,
                movement_points=context.movement_points,
            ),
            enemies_mp=enemies_mp,
            entities_mp=entities_mp,
        )
        movable_mps[context.player_map_point] = context.movement_points

        valid_spells_for_turn = get_valid_spells_for_turn(
            context,
            self.logger,
            allowed_elements=allowed_elements,
        )
        if not valid_spells_for_turn:
            self.logger.info("No valid spells available for this turn")
            return None

        modifiers_map = context.modifier_by_type_and_spell_id
        player_range = context.range

        best_attack: BestAttack | None = None
        weight_cache: dict[WeightCacheKey, float] = {}

        total_candidates = 0
        cast_rejection_stats: dict[RejectionStat, int] = defaultdict(int)
        spells_without_targets = 0

        for spell_lvl, effect, modifiers in valid_spells_for_turn:
            zone_shape = SpellShapeEnum(effect.zoneDescr.shape)
            zone_size = effect.zoneDescr.param1
            zone_alt_size = effect.zoneDescr.param2
            stop_at_target = bool(effect.zoneDescr.isStopAtTarget)
            needs_taken_cell = does_spell_need_taken_cell(spell_lvl) or zone_size == 0

            spell_id = spell_lvl.spellId
            modifier_range_min = modifiers_map.get((spell_id, SpellModifierType.RANGE_MIN))
            modifier_range_max = modifiers_map.get((spell_id, SpellModifierType.RANGE_MAX))
            modifier_cast_line = modifiers_map.get((spell_id, SpellModifierType.CAST_LINE))

            spell_has_targets = False

            for movable_mp, remaining_pm in movable_mps.items():
                zone_spell = get_zone_mps(
                    shape=zone_shape,
                    alternative_size=zone_alt_size,
                    size=zone_size,
                    caster_mp=movable_mp,
                    stop_at_target=stop_at_target,
                )

                targetable_mps = get_possible_mp_spell(
                    movable_mp,
                    spell_lvl,
                    player_range,
                    modifier_range_min=modifier_range_min,
                    modifier_range_max=modifier_range_max,
                    modifier_cast_line=modifier_cast_line,
                )

                if needs_taken_cell:
                    targetable_mps &= entities_mp
                else:
                    targetable_mps = {
                        mp
                        for enemy_mp in enemies_mp
                        for mp in zone_spell.get_mps(enemy_mp, enemy_mp.orientation_to(movable_mp))
                        if mp in targetable_mps
                    }

                for targetable_mp in targetable_mps:
                    cast_result = can_cast_spell_on_mp(
                        context,
                        movable_mp,
                        spell_lvl,
                        targetable_mp,
                        modifiers,
                        entities_mp,
                        entities_id_by_mp,
                        cast_rejection_stats,
                    )
                    if not cast_result:
                        continue

                    direction = movable_mp.orientation_to(targetable_mp)
                    weight_cache_key = WeightCacheKey(spell_lvl, direction, targetable_mp)

                    if weight_cache_key not in weight_cache:
                        impact_mps = zone_spell.get_mps(mp=targetable_mp, direction=direction)
                        weight_cache[weight_cache_key] = calculate_attack_weight(
                            self.damage_calculator,
                            context,
                            impact_mps,
                            spell_lvl,
                            effect,
                            targetable_mp,
                            enemies_data,
                            modifiers,
                        )
                    total_weight = weight_cache[weight_cache_key]
                    spell_has_targets = True
                    total_candidates += 1

                    if best_attack is None or self._is_better_attack(
                        total_weight,
                        remaining_pm,
                        movable_mp,
                        targetable_mp,
                        best_attack,
                    ):
                        best_attack = BestAttack(
                            total_weight,
                            remaining_pm,
                            movable_mp,
                            spell_lvl,
                            targetable_mp,
                        )

            if not spell_has_targets:
                spells_without_targets += 1

        if best_attack is not None and best_attack.total_weight > 0:
            best_spell_name = I18N().name_by_id[
                DataReader().spell_by_id[best_attack.spell_lvl.spellId].nameId
            ]
            self.logger.info(
                f"Attack found: {best_spell_name} -> cell {best_attack.targetable_mp.cell_id} "
                f"from cell {best_attack.movable_mp.cell_id} "
                f"(weight: {best_attack.total_weight:.2f}, {total_candidates} targets evaluated)"
            )
            return (
                best_attack.movable_mp,
                best_attack.spell_lvl,
                best_attack.targetable_mp,
            )

        self._build_debug_info_on_no_attack(spells_without_targets, cast_rejection_stats)

        return None

    def _is_better_attack(
        self,
        weight: float,
        remaining_pm: int,
        from_mp: MapPoint,
        target_mp: MapPoint,
        current_best: tuple[float, int, MapPoint, SpellLevelsRootItem, MapPoint],
    ) -> bool:
        if weight < current_best[0]:
            return False

        if weight > current_best[0]:
            return True

        if remaining_pm < current_best[1]:
            return False

        if remaining_pm > current_best[1]:
            return True

        current_distance = current_best[4].distance_to_map_point(current_best[2])
        new_distance = target_mp.distance_to_map_point(from_mp)
        return new_distance > current_distance

    def _build_debug_info_on_no_attack(
        self,
        spells_without_targets: int,
        cast_rejection_stats: dict[RejectionStat, int],
    ):
        rejection_parts: list[str] = []
        if spells_without_targets > 0:
            rejection_parts.append(f"{spells_without_targets} spells without targets")

        total_cast_rejections = sum(cast_rejection_stats.values())
        if total_cast_rejections > 0:
            cast_stats = ", ".join(f"{k}: {v}" for k, v in cast_rejection_stats.items() if v > 0)
            rejection_parts.append(f"Cast rejections ({cast_stats})")

        if rejection_parts:
            self.logger.debug(f"No attack found - {'; '.join(rejection_parts)}")
        else:
            self.logger.debug("No attack found - no targets evaluated")
