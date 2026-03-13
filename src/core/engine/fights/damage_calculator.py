import math
from dataclasses import dataclass

from DBDofusUnity.datas.protos.non_obf.game.common_pb2 import (
    CharacterCharacteristic,
    SpellModifierType,
)
from DBDofusUnity.dofus_unity_reader.game_constants.characteristic import (
    CharacteristicEnum,
    EffectElement,
)
from DBDofusUnity.dofus_unity_reader.models.datas.monsters_root import MonsterGrade
from DBDofusUnity.dofus_unity_reader.models.datas.spell_levels_root import (
    Effect,
    SpellLevelsRootItem,
)

from src.core.engine.fights.effect import (
    base_roll,
    get_critical_effect,
    resolve_effect_element,
)
from src.core.engine.fights.spell import ModifierMap, spell_modifier_value
from src.core.engine.fights.stats.characteristic import get_stat_by_id


@dataclass(frozen=True)
class _ElementInfo:
    scaling_stat: CharacteristicEnum
    flat_damage_bonus: CharacteristicEnum


ELEMENT_INFO_BY_ID: dict[int, _ElementInfo] = {
    EffectElement.NEUTRAL_ELEMENT: _ElementInfo(
        CharacteristicEnum.STRENGTH, CharacteristicEnum.NEUTRAL_DAMAGE_BONUS
    ),
    EffectElement.STRENGTH: _ElementInfo(CharacteristicEnum.STRENGTH, CharacteristicEnum.EARTH_DAMAGE_BONUS),
    EffectElement.INTELLIGENCE: _ElementInfo(
        CharacteristicEnum.INTELLIGENCE, CharacteristicEnum.FIRE_DAMAGE_BONUS
    ),
    EffectElement.CHANCE: _ElementInfo(CharacteristicEnum.CHANCE, CharacteristicEnum.WATER_DAMAGE_BONUS),
    EffectElement.AGILITY: _ElementInfo(CharacteristicEnum.AGILITY, CharacteristicEnum.AIR_DAMAGE_BONUS),
}


def _multiplier_factor(characteristic_by_id: dict[int, CharacterCharacteristic], stat_id: int) -> float:
    raw = get_stat_by_id(characteristic_by_id.get(stat_id))
    return (raw if raw > 0 else 100) / 100


def _monster_resist_percent(element_id: int, monster_grade: MonsterGrade | None) -> int:
    if monster_grade is None:
        return 0
    bonus = monster_grade.bonusCharacteristics
    match element_id:
        case EffectElement.STRENGTH:
            return monster_grade.earthResistance + bonus.earthResistance
        case EffectElement.INTELLIGENCE:
            return monster_grade.fireResistance + bonus.fireResistance
        case EffectElement.CHANCE:
            return monster_grade.waterResistance + bonus.waterResistance
        case EffectElement.AGILITY:
            return monster_grade.airResistance + bonus.airResistance
        case _:
            return monster_grade.neutralResistance + bonus.neutralResistance


def _percent_factor(
    element_id: int,
    characteristic_by_id: dict[int, CharacterCharacteristic],
    spell_id: int,
    modifiers: ModifierMap | None,
) -> float:
    info = ELEMENT_INFO_BY_ID[element_id]
    bonus = (
        get_stat_by_id(characteristic_by_id.get(info.scaling_stat))
        + get_stat_by_id(characteristic_by_id.get(CharacteristicEnum.POWER))
        + get_stat_by_id(characteristic_by_id.get(CharacteristicEnum.DAMAGES_PERCENT_SPELL))
        + spell_modifier_value(spell_id, SpellModifierType.DAMAGE, modifiers)
    )
    return (100 + bonus) / 100


def _flat_bonus(
    element_id: int,
    characteristic_by_id: dict[int, CharacterCharacteristic],
    is_critical: bool,
) -> int:
    info = ELEMENT_INFO_BY_ID[element_id]
    flat = get_stat_by_id(characteristic_by_id.get(CharacteristicEnum.ALL_DAMAGES_BONUS)) + get_stat_by_id(
        characteristic_by_id.get(info.flat_damage_bonus)
    )
    if is_critical:
        flat += get_stat_by_id(characteristic_by_id.get(CharacteristicEnum.CRITICAL_DAMAGE_BONUS))
    return flat


def _dealt_multipliers(characteristic_by_id: dict[int, CharacterCharacteristic], is_melee: bool) -> float:
    melee_or_distance = (
        CharacteristicEnum.DEALT_DAMAGE_MULTIPLIER_MELEE
        if is_melee
        else CharacteristicEnum.DEALT_DAMAGE_MULTIPLIER_DISTANCE
    )
    return (
        _multiplier_factor(characteristic_by_id, CharacteristicEnum.DEALT_DAMAGE_MULTIPLIER)
        * _multiplier_factor(characteristic_by_id, melee_or_distance)
        * _multiplier_factor(characteristic_by_id, CharacteristicEnum.DEALT_DAMAGE_MULTIPLIER_SPELLS)
    )


def _crit_probability(
    spell_lvl: SpellLevelsRootItem,
    characteristic_by_id: dict[int, CharacterCharacteristic],
) -> float:
    if spell_lvl.criticalHitProbability <= 0 or not spell_lvl.criticalEffect:
        return 0.0
    crit_chance = spell_lvl.criticalHitProbability + get_stat_by_id(
        characteristic_by_id.get(CharacteristicEnum.CRITICAL_HIT)
    )
    return min(max(crit_chance, 0), 100) / 100


def _damage_for_effect(
    effect: Effect,
    element_id: int,
    monster_grade: MonsterGrade | None,
    characteristic_by_id: dict[int, CharacterCharacteristic],
    is_critical: bool,
    modifiers: ModifierMap | None,
) -> float:
    base = base_roll(effect) + spell_modifier_value(effect.spellId, SpellModifierType.BASE_DAMAGE, modifiers)
    raw = base * _percent_factor(element_id, characteristic_by_id, effect.spellId, modifiers) + _flat_bonus(
        element_id, characteristic_by_id, is_critical
    )
    if raw <= 0:
        return 0.0

    raw *= 1 - _monster_resist_percent(element_id, monster_grade) / 100
    return max(raw, 0.0)


@dataclass
class DamageCalculator:
    def get_damage_effect(
        self,
        effect: Effect,
        spell_lvl: SpellLevelsRootItem,
        monster_grade: MonsterGrade | None,
        characteristic_by_id: dict[int, CharacterCharacteristic],
        is_melee: bool,
        primary_elem: EffectElement,
        modifiers: ModifierMap | None = None,
    ) -> int:
        """Predict monster damage; unknown resistance is treated as zero and special redirections are excluded."""
        element_id = resolve_effect_element(effect.effectElement, primary_elem)
        if element_id is None:
            return 0

        multiplier = _dealt_multipliers(characteristic_by_id, is_melee)
        normal_damage = _damage_for_effect(
            effect,
            element_id,
            monster_grade,
            characteristic_by_id,
            is_critical=False,
            modifiers=modifiers,
        )

        crit_probability = _crit_probability(spell_lvl, characteristic_by_id)
        if crit_probability <= 0:
            return math.floor(normal_damage * multiplier)

        crit_damage = _damage_for_effect(
            get_critical_effect(spell_lvl, effect),
            element_id,
            monster_grade,
            characteristic_by_id,
            is_critical=True,
            modifiers=modifiers,
        )
        expected = (1 - crit_probability) * normal_damage + crit_probability * crit_damage
        return math.floor(expected * multiplier)
