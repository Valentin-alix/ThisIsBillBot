from DBDofusUnity.dofus_unity_reader.models.datas.spell_levels_root import (
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


def _self_beneficial_effect(effect: Effect) -> bool:
    return (is_offensive_self_buff_effect(effect) or is_self_shield_effect(effect)) and can_self_cast(effect)


def get_valid_self_buff_spells_for_turn(
    context: AttackContext,
) -> list[tuple[SpellLevelsRootItem, Effect, SpellModifiers]]:
    return collect_castable_spells(context, _self_beneficial_effect, skip_already_cast=True)
