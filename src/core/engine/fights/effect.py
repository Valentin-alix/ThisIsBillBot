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
from dofus_unity_reader.models.datas.spell_levels_root import Effect


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


def get_stat_by_effect_elem(elem: int) -> CharacteristicEnum:
    match elem:
        case EffectElement.CHANCE:
            return CharacteristicEnum.CHANCE
        case EffectElement.STRENGTH:
            return CharacteristicEnum.STRENGTH
        case EffectElement.INTELLIGENCE:
            return CharacteristicEnum.INTELLIGENCE
        case EffectElement.AGILITY:
            return CharacteristicEnum.AGILITY
        case _:
            raise ValueError(f"Unknown elem : {elem} for stat")


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


