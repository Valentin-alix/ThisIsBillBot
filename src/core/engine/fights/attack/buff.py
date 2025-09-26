from dofus_unity_reader.models.datas.spell_levels_root import (
    Effect,
    SpellLevelsRootItem,
)

from src.core.engine.contexts import AttackContext
from src.core.engine.fights.attack.spell_filter import collect_castable_spells
from src.core.engine.fights.effect import (
    can_self_cast,
    is_offensive_self_buff_effect,
    is_self_shield_effect,
)
from src.core.engine.fights.spell_modifier import SpellModifiers
from src.services.logging_utils.loggers import BotLogger


def _self_beneficial_effect(effect: Effect) -> bool:
    return (is_offensive_self_buff_effect(effect) or is_self_shield_effect(effect)) and can_self_cast(effect)


def get_valid_self_buff_spells_for_turn(
    context: AttackContext,
) -> list[tuple[SpellLevelsRootItem, Effect, SpellModifiers]]:
    """Castable beneficial self-casts (offensive buffs and shields), each cast at
    most once per fight (anti-redundancy via ``last_cast_turn_by_spell_id``).
    """
    return collect_castable_spells(context, _self_beneficial_effect, skip_already_cast=True)


def find_best_self_buff(context: AttackContext, logger: BotLogger) -> SpellLevelsRootItem | None:
    best_spell: SpellLevelsRootItem | None = None
    best_ap_cost: int | None = None
    for spell_lvl, _effect, modifiers in get_valid_self_buff_spells_for_turn(context):
        if best_ap_cost is None or modifiers.ap_cost < best_ap_cost:
            best_ap_cost = modifiers.ap_cost
            best_spell = spell_lvl

    if best_spell is not None:
        logger.info(f"Self-buff selected: spell {best_spell.spellId}")
    return best_spell
