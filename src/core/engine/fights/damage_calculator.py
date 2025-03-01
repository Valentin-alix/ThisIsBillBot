import math
from dataclasses import dataclass

from datas.protos.non_obf.game.common_pb2 import (
    CharacterCharacteristic,
)
from dofus_unity_reader.game_constants.characteristic import CharacteristicEnum
from dofus_unity_reader.models.datas.monsters_root import MonsterGrade
from dofus_unity_reader.models.datas.spell_levels_root import Effect

from src.core.engine.fights.effect import get_stat_by_effect_elem
from src.core.engine.fights.stats.characteristic import get_stat_by_id


@dataclass
class DamageCalculator:
    def get_damage_effect(
        self,
        effect: Effect,
        monster_grade: MonsterGrade,
        characteristic_by_id: dict[int, CharacterCharacteristic],
    ) -> int:
        """Predict how much dmg an Effect will do to a monster"""
        related_stat = get_stat_by_effect_elem(effect.effectElement)

        power = get_stat_by_id(characteristic_by_id.get(CharacteristicEnum.POWER))

        match related_stat:
            case CharacteristicEnum.CHANCE:
                resistance_stat_percent = monster_grade.waterResistance
                fixed_damage_stat = get_stat_by_id(
                    characteristic_by_id.get((CharacteristicEnum.WATER_DAMAGE_BONUS))
                )
            case CharacteristicEnum.AGILITY:
                resistance_stat_percent = monster_grade.airResistance
                fixed_damage_stat = get_stat_by_id(
                    characteristic_by_id.get((CharacteristicEnum.AIR_DAMAGE_BONUS))
                )
            case CharacteristicEnum.STRENGTH:
                resistance_stat_percent = monster_grade.airResistance
                fixed_damage_stat = get_stat_by_id(
                    characteristic_by_id.get((CharacteristicEnum.EARTH_DAMAGE_BONUS))
                )
            case CharacteristicEnum.INTELLIGENCE:
                resistance_stat_percent = monster_grade.fireResistance
                fixed_damage_stat = get_stat_by_id(
                    characteristic_by_id.get((CharacteristicEnum.FIRE_DAMAGE_BONUS))
                )
            case _:
                return 0

        stat_char = get_stat_by_id(characteristic_by_id.get((related_stat)))
        fixed_damage = get_stat_by_id(
            characteristic_by_id.get((CharacteristicEnum.ALL_DAMAGES_BONUS))
        )

        damage = (
            effect.diceNum * (100 + stat_char + power) / 100
            + (fixed_damage_stat + fixed_damage)
        ) * (1 - resistance_stat_percent / 100)

        return math.floor(damage)
