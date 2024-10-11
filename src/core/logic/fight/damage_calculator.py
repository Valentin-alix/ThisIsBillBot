from models.datas.spell_levels_root import Effect


class DamageCalculator:
    @staticmethod
    def get_damage_effect(effect: Effect) -> float:
        return (effect.diceNum + effect.diceSide) / 2
