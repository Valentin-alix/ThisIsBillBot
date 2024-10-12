from models.datas.spell_levels_root import Effect
from src.core.data_center.data_reader import DataReader
from src.interfaces.enums.characteristic_enum import CharacteristicEnum
from src.interfaces.enums.effect_element import EffectElement


def is_primary_attack_elem(effect: Effect, primary_elem: EffectElement):
    if effect.effectElement == primary_elem:
        data_effect = DataReader().effect_by_id[effect.effectId]
        return data_effect.characteristicOperator == ""


def get_effect_elem_by_stat(stat_id: int):
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


def get_stat_by_effect_elem(elem: int):
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
