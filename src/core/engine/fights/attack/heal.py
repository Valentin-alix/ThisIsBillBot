import math

from dofus_unity_reader.data_center.data_reader import DataReader
from dofus_unity_reader.game_constants.characteristic import CharacteristicEnum
from dofus_unity_reader.game_constants.description import DescriptionEnum
from dofus_unity_reader.models.datas.spell_levels_root import (
    Effect,
    SpellLevelsRootItem,
)

from src.core.engine.contexts import AttackContext
from src.core.engine.fights.attack.spell_filter import collect_castable_spells
from src.core.engine.fights.effect import base_roll, can_self_cast, is_heal_effect
from src.core.engine.fights.spell_modifier import SpellModifiers
from src.core.engine.fights.stats.characteristic import get_stat_by_id
from src.services.logging_utils.loggers import BotLogger

# Only consider healing below this fraction of max HP, and only when a single cast
# restores at least MIN_HEAL_FRACTION of max HP (avoids wasting AP on tiny heals).
HEAL_HP_THRESHOLD = 0.5
MIN_HEAL_FRACTION = 0.05


def estimate_self_heal(effect: Effect, context: AttackContext) -> int:
    """Rough expected heal amount on the caster, by heal type."""
    description_id = DataReader().effect_by_id[effect.effectId].descriptionId
    heal_bonus = get_stat_by_id(
        context.characteristic_by_id.get(CharacteristicEnum.HEAL_BONUS)
    )
    base = base_roll(effect)

    if description_id == DescriptionEnum.HEAL_PERCENT_MAX_LIFE:
        return math.floor(base / 100 * context.max_life_point + heal_bonus)
    if description_id == DescriptionEnum.HEAL_FLAT_LIFE:
        return math.floor(base + heal_bonus)

    # Elemental heals scale on a primary stat (Intelligence dominates in practice);
    # a rough approximation is enough to prioritise.
    intelligence = get_stat_by_id(
        context.characteristic_by_id.get(CharacteristicEnum.INTELLIGENCE)
    )
    return math.floor(base * (100 + intelligence) / 100 + heal_bonus)


def _self_heal_effect(effect: Effect) -> bool:
    return is_heal_effect(effect) and can_self_cast(effect)


def get_valid_heal_spells_for_turn(
    context: AttackContext,
) -> list[tuple[SpellLevelsRootItem, Effect, SpellModifiers]]:
    return collect_castable_spells(context, _self_heal_effect)


def find_best_self_heal(
    context: AttackContext, logger: BotLogger
) -> SpellLevelsRootItem | None:
    """Pick the most efficient self-heal (healed HP per AP) when HP is low.

    Returns None when the caster is healthy enough, no heal is castable, or every
    castable heal would restore a negligible amount.
    """
    if context.life_percentage >= HEAL_HP_THRESHOLD:
        return None
    missing = context.max_life_point - context.life_point
    if missing <= 0:
        return None
    min_useful = context.max_life_point * MIN_HEAL_FRACTION

    best_spell: SpellLevelsRootItem | None = None
    best_weight = 0.0
    for spell_lvl, effect, modifiers in get_valid_heal_spells_for_turn(context):
        effective = min(estimate_self_heal(effect, context), missing)
        if effective < min_useful:
            continue
        weight = effective / modifiers.ap_cost
        if weight > best_weight:
            best_weight = weight
            best_spell = spell_lvl

    if best_spell is not None:
        logger.info(
            f"Self-heal selected: spell {best_spell.spellId} "
            f"(weight {best_weight:.1f}, missing {missing} HP)"
        )
    return best_spell
