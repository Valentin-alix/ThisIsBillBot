from models.datas.spell_levels_root import Effect
from src.core.data_center.data_reader import DataReader
from src.interfaces.enums.effect_element import EffectElement


def is_primary_attack_elem(effect: Effect, primary_elem: EffectElement):
    if effect.effectElement == primary_elem:
        data_effect = DataReader().effect_by_id[effect.effectId]
        return data_effect.characteristicOperator == ""
