from collections import defaultdict
from dataclasses import dataclass
from typing import NamedTuple

from DBDofusUnity.datas.protos.non_obf.game.common_pb2 import SpellModifier, SpellModifierType
from DBDofusUnity.dofus_unity_reader.data_center.data_reader import DataReader
from DBDofusUnity.dofus_unity_reader.data_center.i18n import I18N
from DBDofusUnity.dofus_unity_reader.game_constants.directions import DirectionsEnum
from DBDofusUnity.dofus_unity_reader.game_constants.spell_shape_enum import SpellShapeEnum
from DBDofusUnity.dofus_unity_reader.grid.map_point import MapPoint
from DBDofusUnity.dofus_unity_reader.models.datas.spell_levels_root import Effect, SpellLevelsRootItem
from src.core.engine.contexts import AttackContext
from src.core.engine.fights.attack.buff import get_valid_self_buff_spells_for_turn
from src.core.engine.fights.attack.cast_validator import can_cast_spell_on_mp
from src.core.engine.fights.attack.enemy_data import EnemyData
from src.core.engine.fights.attack.heal import (
    HEAL_HP_THRESHOLD,
    estimate_self_heal,
    get_valid_heal_spells_for_turn,
)
from src.core.engine.fights.attack.positions import AttackPositions, get_movable_mps, get_positions
from src.core.engine.fights.attack.rejection_stat import RejectionStat
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
from src.core.engine.fights.spell_modifier import SpellModifiers
from src.core.engine.fights.spell_zone import get_zone_mps
from src.core.engine.fights.zones.zone import Zone
from src.services.logging_utils.contextual_logger import ContextualLogger

ModifiersMap = dict[tuple[int, SpellModifierType], SpellModifier]
ValidSpellsForTurn = list[tuple[SpellLevelsRootItem, Effect, SpellModifiers]]


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

    def find_best_attack_from_mp(
        self, context: AttackContext
    ) -> tuple[MapPoint, SpellLevelsRootItem, MapPoint] | None:
        positions = get_positions(context)
        movable_mps = get_movable_mps(context, positions, self.fight_reachable_cells)

        valid_spells_for_turn = get_valid_spells_for_turn(context, self.logger)
        if not valid_spells_for_turn:
            self.logger.info("No valid spells available for this turn")
            return None

        best_attack, total_candidates, spells_without_targets, cast_rejection_stats = self._get_best_attack(
            context,
            valid_spells_for_turn,
            movable_mps,
            positions,
            context.modifier_by_type_and_spell_id,
            context.range,
        )

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

    def _get_targetable_mps(
        self,
        movable_mp: MapPoint,
        spell_lvl: SpellLevelsRootItem,
        zone_spell: Zone,
        needs_taken_cell: bool,
        positions: AttackPositions,
        player_range: int,
        modifiers_map: ModifiersMap,
    ) -> set[MapPoint]:
        spell_id = spell_lvl.spellId
        targetable_mps = get_possible_mp_spell(
            movable_mp,
            spell_lvl,
            player_range,
            modifier_range_min=modifiers_map.get((spell_id, SpellModifierType.RANGE_MIN)),
            modifier_range_max=modifiers_map.get((spell_id, SpellModifierType.RANGE_MAX)),
            modifier_cast_line=modifiers_map.get((spell_id, SpellModifierType.CAST_LINE)),
        )

        if needs_taken_cell:
            return targetable_mps & positions.entities_mp

        return {
            mp
            for enemy_mp in positions.enemies_mp
            for mp in zone_spell.get_mps(enemy_mp, enemy_mp.orientation_to(movable_mp))
            if mp in targetable_mps
        }

    def _get_candidate_weight(
        self,
        context: AttackContext,
        movable_mp: MapPoint,
        spell_lvl: SpellLevelsRootItem,
        effect: Effect,
        targetable_mp: MapPoint,
        zone_spell: Zone,
        modifiers: SpellModifiers,
        positions: AttackPositions,
        enemies_data: list[EnemyData],
        weight_cache: dict[WeightCacheKey, float],
        cast_rejection_stats: dict[RejectionStat, int],
    ) -> float | None:
        cast_result = can_cast_spell_on_mp(
            context,
            movable_mp,
            spell_lvl,
            targetable_mp,
            modifiers,
            positions.entities_mp,
            positions.entities_id_by_mp,
            cast_rejection_stats,
        )
        if not cast_result:
            return None

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
        return weight_cache[weight_cache_key]

    def _get_best_attack(
        self,
        context: AttackContext,
        valid_spells_for_turn: ValidSpellsForTurn,
        movable_mps: dict[MapPoint, int],
        positions: AttackPositions,
        modifiers_map: ModifiersMap,
        player_range: int,
    ) -> tuple[BestAttack | None, int, int, dict[RejectionStat, int]]:
        enemies_data = context.enemies_data
        best_attack: BestAttack | None = None
        weight_cache: dict[WeightCacheKey, float] = {}

        total_candidates = 0
        cast_rejection_stats: dict[RejectionStat, int] = defaultdict(int)
        spells_without_targets = 0

        for spell_lvl, effect, modifiers in valid_spells_for_turn:
            zone_size = effect.zoneDescr.param1
            needs_taken_cell = does_spell_need_taken_cell(spell_lvl) or zone_size == 0
            zone_spell_factory = SpellShapeEnum(effect.zoneDescr.shape)
            spell_has_targets = False

            for movable_mp, remaining_pm in movable_mps.items():
                zone_spell = get_zone_mps(
                    shape=zone_spell_factory,
                    alternative_size=effect.zoneDescr.param2,
                    size=zone_size,
                    caster_mp=movable_mp,
                    stop_at_target=bool(effect.zoneDescr.isStopAtTarget),
                )

                targetable_mps = self._get_targetable_mps(
                    movable_mp,
                    spell_lvl,
                    zone_spell,
                    needs_taken_cell,
                    positions,
                    player_range,
                    modifiers_map,
                )

                for targetable_mp in targetable_mps:
                    weight = self._get_candidate_weight(
                        context,
                        movable_mp,
                        spell_lvl,
                        effect,
                        targetable_mp,
                        zone_spell,
                        modifiers,
                        positions,
                        enemies_data,
                        weight_cache,
                        cast_rejection_stats,
                    )
                    if weight is None:
                        continue

                    spell_has_targets = True
                    total_candidates += 1

                    if best_attack is None or self._is_better_attack(
                        weight,
                        remaining_pm,
                        movable_mp,
                        targetable_mp,
                        best_attack,
                    ):
                        best_attack = BestAttack(
                            weight,
                            remaining_pm,
                            movable_mp,
                            spell_lvl,
                            targetable_mp,
                        )

            if not spell_has_targets:
                spells_without_targets += 1

        return best_attack, total_candidates, spells_without_targets, cast_rejection_stats

    def find_best_self_heal(self, context: AttackContext) -> SpellLevelsRootItem | None:
        if context.life_percentage >= HEAL_HP_THRESHOLD:
            return None
        missing = context.max_life_point - context.life_point
        if missing <= 0:
            return None

        best_spell: SpellLevelsRootItem | None = None
        best_weight = 0.0
        for spell_lvl, effect, modifiers in get_valid_heal_spells_for_turn(context):
            effective = min(estimate_self_heal(effect, context), missing)
            weight = effective / modifiers.ap_cost
            if weight > best_weight:
                best_weight = weight
                best_spell = spell_lvl

        if best_spell is not None:
            self.logger.info(
                f"Self-heal selected: spell {best_spell.spellId} (weight {best_weight:.1f}, missing {missing} HP)"
            )
        return best_spell

    def find_best_self_buff(self, context: AttackContext) -> SpellLevelsRootItem | None:
        best_spell: SpellLevelsRootItem | None = None
        best_ap_cost: int | None = None
        for spell_lvl, _effect, modifiers in get_valid_self_buff_spells_for_turn(context):
            if best_ap_cost is None or modifiers.ap_cost < best_ap_cost:
                best_ap_cost = modifiers.ap_cost
                best_spell = spell_lvl

        if best_spell is not None:
            self.logger.info(f"Self-buff selected: spell {best_spell.spellId}")
        return best_spell

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
