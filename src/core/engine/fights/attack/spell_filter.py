from collections import defaultdict
from collections.abc import Callable

from DBDofusUnity.dofus_unity_reader.data_center.data_reader import DataReader
from DBDofusUnity.dofus_unity_reader.models.datas.spell_levels_root import (
    Effect,
    SpellLevelsRootItem,
)
from src.core.engine.contexts import AttackContext
from src.core.engine.fights.attack.rejection_stat import RejectionStat
from src.core.engine.fights.spell import get_damage_spells
from src.core.engine.fights.spell_modifier import SpellModifiers
from src.services.logging_utils.loggers import BotLogger


def get_valid_spells_for_turn(
    context: AttackContext,
    logger: BotLogger,
) -> list[tuple[SpellLevelsRootItem, Effect, SpellModifiers]]:
    valuable_spells = get_damage_spells(context.spells, context.primary_elem)

    rejection_stats: dict[RejectionStat, int] = defaultdict(int)

    valid_spell_levels: list[tuple[SpellLevelsRootItem, Effect, SpellModifiers]] = []
    modifiers_map = context.modifier_by_type_and_spell_id

    for spell_lvl, effect in valuable_spells:
        modifiers = SpellModifiers.from_spell(
            context.range,
            spell_lvl,
            modifiers_map,
        )
        if is_spell_valid_for_turn(context, spell_lvl, modifiers, rejection_stats):
            valid_spell_levels.append((spell_lvl, effect, modifiers))

    total_rejected = sum(rejection_stats.values())
    if total_rejected > 0:
        stats_str = ", ".join(f"{k}: {v}" for k, v in rejection_stats.items() if v > 0)
        logger.info(
            f"Spell validation: {len(valid_spell_levels)}/{len(valuable_spells)} valid "
            f"(AP: {context.action_points}) - Rejected: {stats_str}"
        )
    else:
        logger.info(
            f"Spell validation: {len(valid_spell_levels)}/{len(valuable_spells)} valid "
            f"(AP: {context.action_points})"
        )

    return valid_spell_levels


def collect_castable_spells(
    context: AttackContext,
    effect_predicate: Callable[[Effect], bool],
) -> list[tuple[SpellLevelsRootItem, Effect, SpellModifiers]]:
    rejection_stats: dict[RejectionStat, int] = defaultdict(int)
    valid: list[tuple[SpellLevelsRootItem, Effect, SpellModifiers]] = []
    modifiers_map = context.modifier_by_type_and_spell_id

    for spell in context.spells:
        if not spell.spell_id:
            continue
        spell_lvl = DataReader().spell_lvl_by_spell_id[spell.spell_id][spell.spell_level - 1]
        matched = next((effect for effect in spell_lvl.effects if effect_predicate(effect)), None)
        if matched is None:
            continue
        modifiers = SpellModifiers.from_spell(context.range, spell_lvl, modifiers_map)
        if is_spell_valid_for_turn(context, spell_lvl, modifiers, rejection_stats):
            valid.append((spell_lvl, matched, modifiers))

    return valid


def resolve_castable_spell_lvl(context: AttackContext, spell_id: int) -> SpellLevelsRootItem | None:
    spell = next((spell for spell in context.spells if spell.spell_id == spell_id), None)
    if spell is None:
        return None

    spell_lvl = DataReader().spell_lvl_by_spell_id[spell.spell_id][spell.spell_level - 1]
    modifiers = SpellModifiers.from_spell(context.range, spell_lvl, context.modifier_by_type_and_spell_id)
    rejection_stats: dict[RejectionStat, int] = defaultdict(int)
    if not is_spell_valid_for_turn(context, spell_lvl, modifiers, rejection_stats):
        return None

    return spell_lvl


def is_spell_valid_for_turn(
    context: AttackContext,
    spell_lvl: SpellLevelsRootItem,
    modifiers: SpellModifiers,
    rejection_stats: dict[RejectionStat, int],
) -> bool:
    current_ap = context.action_points

    if modifiers.ap_cost > current_ap:
        rejection_stats[RejectionStat.INSUFICIENT_AP] += 1
        return False

    if spell_lvl.initialCooldown != 0 and context.fight_turn <= spell_lvl.initialCooldown:
        rejection_stats[RejectionStat.INITIAL_COOLDOWN] += 1
        return False

    last_cast_turn = context.cast_turn_by_spell_id.get(spell_lvl.spellId)
    if (
        spell_lvl.globalCooldown != 0
        and last_cast_turn is not None
        and context.fight_turn - last_cast_turn < spell_lvl.globalCooldown
    ):
        rejection_stats[RejectionStat.GLOBAL_COOLDOWN] += 1
        return False

    if (
        spell_lvl.minCastInterval != 0
        and last_cast_turn is not None
        and context.fight_turn - last_cast_turn < spell_lvl.minCastInterval
    ):
        rejection_stats[RejectionStat.MIN_CAST_INTERVAL] += 1
        return False

    count_casted = context.count_casted_by_spell_id_on_current_turn.get(spell_lvl.spellId)
    if (
        count_casted is not None
        and modifiers.max_cast_per_turn != 0
        and modifiers.max_cast_per_turn <= count_casted
    ):
        rejection_stats[RejectionStat.MAX_CAST_PER_TURN] += 1
        return False

    if spell_lvl.maxStack > 0:
        active_stacks = context.own_active_stack_count_by_spell_id.get(spell_lvl.spellId, 0)
        if active_stacks >= spell_lvl.maxStack:
            rejection_stats[RejectionStat.MAX_STACK_REACHED] += 1
            return False

    return True
