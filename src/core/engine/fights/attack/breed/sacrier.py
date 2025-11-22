from collections import defaultdict

from DBDofusUnity.datas.protos.non_obf.game.common_pb2 import SpellModifierType
from DBDofusUnity.dofus_unity_reader.grid.map_point import MapPoint
from DBDofusUnity.dofus_unity_reader.models.datas.spell_levels_root import SpellLevelsRootItem
from src.core.engine.contexts import AttackContext
from src.core.engine.fights.attack.breed.types import SupportAction, SupportActionRule
from src.core.engine.fights.attack.cast_validator import can_cast_spell_on_mp
from src.core.engine.fights.attack.lethality import can_finish_fight_this_turn
from src.core.engine.fights.attack.positions import get_movable_mps, get_positions
from src.core.engine.fights.attack.rejection_stat import RejectionStat
from src.core.engine.fights.attack.spell_filter import resolve_castable_spell_lvl
from src.core.engine.fights.damage_calculator import DamageCalculator
from src.core.engine.fights.reachable_cells.fight_reachable_cells import FightReachableCells
from src.core.engine.fights.spell import get_possible_mp_spell
from src.core.engine.fights.spell_modifier import SpellModifiers

SACRIER_EPEE_VORACE_SPELL_ID = 12744
SACRIER_MUTILATION_SPELL_ID = 12737
MUTILATION_INITIAL_CAST_LIFE_THRESHOLD = 0.50
MUTILATION_RECAST_LIFE_THRESHOLD = 0.30


def _resolve_invocation_spell_lvl(
    context: AttackContext, damage_calculator: DamageCalculator
) -> SpellLevelsRootItem | None:
    if can_finish_fight_this_turn(context, damage_calculator):
        return None
    if context.own_active_summon_count >= context.max_active_summon_count:
        return None
    return resolve_castable_spell_lvl(context, SACRIER_EPEE_VORACE_SPELL_ID)


def get_reserved_ap(context: AttackContext, damage_calculator: DamageCalculator) -> int:
    """AP the attack search should hold back so the invocation still has its AP."""
    spell_lvl = _resolve_invocation_spell_lvl(context, damage_calculator)
    if spell_lvl is None:
        return 0
    return SpellModifiers.from_spell(context.range, spell_lvl, context.modifier_by_type_and_spell_id).ap_cost


def _find_invocation(
    context: AttackContext, fight_reachable_cells: FightReachableCells, damage_calculator: DamageCalculator
) -> SupportAction | None:
    """Not a self-cast: line-cast at range 1-3 onto an empty, LOS-visible cell."""
    spell_lvl = _resolve_invocation_spell_lvl(context, damage_calculator)
    if spell_lvl is None:
        return None

    positions = get_positions(context)
    movable_mps = get_movable_mps(context, positions, fight_reachable_cells)
    modifiers = SpellModifiers.from_spell(context.range, spell_lvl, context.modifier_by_type_and_spell_id)
    modifiers_map = context.modifier_by_type_and_spell_id
    spell_id = spell_lvl.spellId

    rejection_stats: dict[RejectionStat, int] = defaultdict(int)
    best_key: tuple[float, int] | None = None
    best: tuple[MapPoint, MapPoint] | None = None
    for movable_mp, remaining_pm in movable_mps.items():
        candidate_mps = get_possible_mp_spell(
            movable_mp,
            spell_lvl,
            context.range,
            modifier_range_min=modifiers_map.get((spell_id, SpellModifierType.RANGE_MIN)),
            modifier_range_max=modifiers_map.get((spell_id, SpellModifierType.RANGE_MAX)),
            modifier_cast_line=modifiers_map.get((spell_id, SpellModifierType.CAST_LINE)),
        )
        for target_mp in candidate_mps:
            if target_mp in positions.entities_mp:
                continue
            if not can_cast_spell_on_mp(
                context,
                movable_mp,
                spell_lvl,
                target_mp,
                modifiers,
                positions.entities_mp,
                positions.entities_id_by_mp,
                rejection_stats,
            ):
                continue

            dist_to_nearest_enemy = min(
                target_mp.distance_to_map_point(enemy_mp) for enemy_mp in positions.enemies_mp
            )
            key = (dist_to_nearest_enemy, -remaining_pm)
            if best_key is None or key < best_key:
                best_key = key
                best = (movable_mp, target_mp)

    if best is None:
        return None

    movable_mp, target_mp = best
    return movable_mp, spell_lvl, target_mp


def _mutilation_self_cast(context: AttackContext) -> SupportAction | None:
    spell_lvl = resolve_castable_spell_lvl(context, SACRIER_MUTILATION_SPELL_ID)
    if spell_lvl is None:
        return None
    return context.player_map_point, spell_lvl, context.player_map_point


def _find_mutilation_initial_cast(
    context: AttackContext, _fight_reachable_cells: FightReachableCells, damage_calculator: DamageCalculator
) -> SupportAction | None:
    if can_finish_fight_this_turn(context, damage_calculator):
        return None
    if context.life_percentage <= MUTILATION_INITIAL_CAST_LIFE_THRESHOLD:
        return None
    if SACRIER_MUTILATION_SPELL_ID in context.cast_turn_by_spell_id:
        return None

    return _mutilation_self_cast(context)


def _find_mutilation_recast(
    context: AttackContext, _fight_reachable_cells: FightReachableCells, damage_calculator: DamageCalculator
) -> SupportAction | None:
    if can_finish_fight_this_turn(context, damage_calculator):
        return None
    if SACRIER_MUTILATION_SPELL_ID not in context.cast_turn_by_spell_id:
        return None
    if context.life_percentage > MUTILATION_RECAST_LIFE_THRESHOLD:
        return None

    return _mutilation_self_cast(context)


RULES: list[SupportActionRule] = [_find_invocation]
URGENT_RULES: list[SupportActionRule] = [_find_mutilation_initial_cast, _find_mutilation_recast]
