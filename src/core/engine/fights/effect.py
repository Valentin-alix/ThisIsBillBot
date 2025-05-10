from typing import Callable

from datas.protos.non_obf.game.common_pb2 import (
    ActorPositionInformation,
    Team,
)
from dofus_unity_reader.data_center.data_reader import DataReader
from dofus_unity_reader.data_center.i18n import I18N
from dofus_unity_reader.game_constants.characteristic import (
    CharacteristicEnum,
    EffectElement,
    TypeEffect,
)
from dofus_unity_reader.game_constants.description import DescriptionEnum
from dofus_unity_reader.models.datas.spell_levels_root import (
    Effect,
    SpellLevelsRootItem,
)

# Effect.effectElement: 5 == "best element of the caster"
BEST_ELEMENT = 5


def _has_description(effect: Effect, description_ids: frozenset[int]) -> bool:
    """Whether the effect's definition descriptionId is in ``description_ids``.

    descriptionId is a stable, numeric, language-agnostic effect-role signal.
    """
    return DataReader().effect_by_id[effect.effectId].descriptionId in description_ids


HEAL_DESCRIPTION_IDS: frozenset[int] = frozenset(
    {
        DescriptionEnum.HEAL_FLAT_LIFE,
        DescriptionEnum.HEAL_PERCENT_MAX_LIFE,
        DescriptionEnum.HEAL_FIXED,
        DescriptionEnum.HEAL_PLAIN,
        DescriptionEnum.HEAL_SINGLE,
        DescriptionEnum.HEAL_WATER,
        DescriptionEnum.HEAL_AIR,
        DescriptionEnum.HEAL_EARTH,
        DescriptionEnum.HEAL_NEUTRAL,
        DescriptionEnum.HEAL_BEST_ELEMENT,
        DescriptionEnum.HEAL_FIRE,
        DescriptionEnum.HEAL_ELEMENTAL,
    }
)


def is_heal_effect(effect: Effect) -> bool:
    """Whether an effect directly restores life points.

    ``category`` alone is not a reliable discriminator: heals span categories 0
    and 2, and category 2 also contains damage-conditional heals we exclude.
    """
    return _has_description(effect, HEAL_DESCRIPTION_IDS)


# "Repousse de N cases" effects that deal collision damage (push distance =
# effect.diceNum). Excludes the "(sans dommages)" and the pull ("Attire") variants.
PUSH_DESCRIPTION_IDS: frozenset[int] = frozenset(
    {
        DescriptionEnum.PUSH,
        DescriptionEnum.PUSH_ALT,
        DescriptionEnum.PUSH_FORCED,
        DescriptionEnum.PUSH_FORCED_ALT,
    }
)


def is_push_effect(effect: Effect) -> bool:
    """Whether an effect pushes the target away and can deal collision damage."""
    return _has_description(effect, PUSH_DESCRIPTION_IDS)


# Positive self-buff effects worth casting before attacking (boost damage output
# or AP). Their malus counterparts have distinct descriptionIds (leading "-").
OFFENSIVE_SELF_BUFF_DESCRIPTION_IDS: frozenset[int] = frozenset(
    {
        DescriptionEnum.BUFF_POWER,
        DescriptionEnum.BUFF_SPELL_POWER,
        DescriptionEnum.BUFF_DAMAGE,
        DescriptionEnum.BUFF_ACTION_POINTS,
    }
)


def is_offensive_self_buff_effect(effect: Effect) -> bool:
    """Whether an effect is a beneficial offensive buff (Power/Damage/AP gain)."""
    return _has_description(effect, OFFENSIVE_SELF_BUFF_DESCRIPTION_IDS)


# Shield effects (flat, %-of-level, %-of-max-life) — a defensive buff.
SHIELD_DESCRIPTION_IDS: frozenset[int] = frozenset(
    {
        DescriptionEnum.SHIELD_FLAT,
        DescriptionEnum.SHIELD_PERCENT_LEVEL,
        DescriptionEnum.SHIELD_PERCENT_MAX_LIFE,
    }
)


def is_self_shield_effect(effect: Effect) -> bool:
    """Whether an effect grants a damage-absorbing shield."""
    return _has_description(effect, SHIELD_DESCRIPTION_IDS)


def resolve_effect_element(
    effect_element: int, primary_elem: EffectElement
) -> int | None:
    """Resolve ``effectElement`` to a concrete element id, or None if non-damage.

    The "best element" sentinel (5) is mapped to the caster's primary element.
    """
    if effect_element == BEST_ELEMENT:
        return primary_elem
    if effect_element in EffectElement:
        return effect_element
    return None


def get_effect_elem_by_stat(stat_id: int) -> EffectElement:
    match stat_id:
        case CharacteristicEnum.CHANCE:
            return EffectElement.CHANCE
        case CharacteristicEnum.STRENGTH:
            return EffectElement.STRENGTH
        case CharacteristicEnum.INTELLIGENCE:
            return EffectElement.INTELLIGENCE
        case CharacteristicEnum.AGILITY:
            return EffectElement.AGILITY
        case _:
            raise ValueError(f"Unknown primary stat : {stat_id} for elem")


def get_type_effect(spell_id: int, effect: Effect) -> TypeEffect | None:
    data_effect = DataReader().effect_by_id[effect.effectId]
    description_spell = I18N().name_by_id[
        DataReader().spell_by_id[spell_id].descriptionId
    ]
    if (
        DescriptionEnum.MALUS_LIFE_PERCENT == data_effect.descriptionId
        and "vie du lanceur" in description_spell.lower()
        and data_effect.isInPercent
    ):
        return TypeEffect.MALUS_LIFE_PERCENT
    if DescriptionEnum.SHIELD_PERCENT_LEVEL == data_effect.descriptionId:
        return TypeEffect.SHIELD_PERCENT_LEVEL


def get_life_point_percent_malus(life_point: int, effect: Effect) -> int:
    return int(life_point * effect.diceNum / 100)


def get_effect_shield_level_bonus(level: int, effect: Effect) -> int:
    return int(level * effect.diceNum / 100)


def is_included_by_mask(
    caster_id: int,
    caster_team: Team,
    masks: list[str],
    target_actor: ActorPositionInformation,
) -> bool:
    if target_actor.actor_id == caster_id:
        if any(char in masks for char in ("c", "C", "a")):
            return True

    is_same_team = (
        caster_team == target_actor.actor_information.fighter.spawn_information.team
    )

    is_summoned_target = False

    conditions: dict[str, Callable[[], bool]] = {
        "A": lambda: not is_same_team,
        "D": lambda: not is_same_team,
        "H": lambda: not is_same_team and not is_summoned_target,
        "I": lambda: not is_same_team and is_summoned_target,
        "J": lambda: not is_same_team and is_summoned_target,
        "L": lambda: not is_same_team and not is_summoned_target,
        "M": lambda: not is_same_team and not is_summoned_target,
        "S": lambda: not is_same_team and is_summoned_target,
        "d": lambda: is_same_team,
        "h": lambda: is_same_team and not is_summoned_target,
        "i": lambda: is_same_team and is_summoned_target,
        "j": lambda: is_same_team and is_summoned_target,
        "l": lambda: is_same_team and not is_summoned_target,
        "m": lambda: is_same_team and not is_summoned_target,
        "s": lambda: is_same_team and is_summoned_target,
        "g": lambda: is_same_team,
        "a": lambda: is_same_team,
    }

    return any(conditions.get(mask, lambda: False)() for mask in masks)


def get_critical_effect(spell_lvl: SpellLevelsRootItem, effect: Effect) -> Effect:
    for crit_effect in spell_lvl.criticalEffect:
        if crit_effect.effectElement == effect.effectElement:
            return crit_effect
    return effect


def base_roll(effect: Effect) -> float:
    """Average roll: diceNum=min, diceSide=max, value=fixed when both dice are 0."""
    if effect.diceNum == 0 and effect.diceSide == 0:
        return float(effect.value)
    if effect.diceSide > effect.diceNum:
        return (effect.diceNum + effect.diceSide) / 2
    return float(effect.diceNum)


# targetMask characters that include the caster itself.
_SELF_MASK_CHARS = ("C", "c", "a")

# targetMask characters that can apply to enemy fighters.
_ENEMY_MASK_CHARS = frozenset({"A", "D", "H", "I", "J", "L", "M", "S"})


def can_self_cast(effect: Effect) -> bool:
    return any(char in effect.targetMask for char in _SELF_MASK_CHARS)


def can_target_enemy(effect: Effect) -> bool:
    return any(char in _ENEMY_MASK_CHARS for char in effect.targetMask)
