import math
from dataclasses import dataclass

from models.datas.monsters_root import MonsterGrade
from models.datas.spell_levels_root import Effect
from src.core.logic.fight.effect import get_stat_by_effect_elem
from src.core.states.game_state import GameState
from enums.characteristic_enum import CharacteristicEnum


@dataclass
class DamageCalculator:
    game_state: GameState

    def get_damage_effect(
        self, effect: Effect, monster_grade: MonsterGrade | None
    ) -> int:
        related_stat = get_stat_by_effect_elem(effect.effectElement)
        stat_char = self.game_state.player.get_player_stat_by_id(related_stat)
        power = 0
        fixed_damage = self.game_state.player.get_player_stat_by_id(
            CharacteristicEnum.ALL_DAMAGES_BONUS
        )
        match related_stat:
            case CharacteristicEnum.CHANCE:
                resistance_stat_percent = (
                    monster_grade.waterResistance if monster_grade else 0
                )
                fixed_damage_stat = self.game_state.player.get_player_stat_by_id(
                    CharacteristicEnum.WATER_DAMAGE_BONUS
                )
            case CharacteristicEnum.AGILITY:
                resistance_stat_percent = (
                    monster_grade.airResistance if monster_grade else 0
                )
                fixed_damage_stat = self.game_state.player.get_player_stat_by_id(
                    CharacteristicEnum.AIR_DAMAGE_BONUS
                )
            case CharacteristicEnum.STRENGTH:
                resistance_stat_percent = (
                    monster_grade.airResistance if monster_grade else 0
                )
                fixed_damage_stat = self.game_state.player.get_player_stat_by_id(
                    CharacteristicEnum.EARTH_DAMAGE_BONUS
                )
            case CharacteristicEnum.INTELLIGENCE:
                resistance_stat_percent = (
                    monster_grade.fireResistance if monster_grade else 0
                )
                fixed_damage_stat = self.game_state.player.get_player_stat_by_id(
                    CharacteristicEnum.FIRE_DAMAGE_BONUS
                )
            case _:
                resistance_stat_percent = 0
                fixed_damage_stat = 0

        damage = (
            effect.diceNum * (100 + stat_char + power) / 100
            + (fixed_damage_stat + fixed_damage)
        ) * (1 - resistance_stat_percent / 100)

        return math.floor(damage)
