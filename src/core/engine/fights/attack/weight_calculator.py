import re
from functools import cache

from dofus_unity_reader.data_center.data_reader import DataReader
from dofus_unity_reader.data_center.i18n import I18N
from dofus_unity_reader.game_constants.characteristic import TypeEffect
from dofus_unity_reader.grid.map_point import MapPoint
from dofus_unity_reader.models.datas.spell_levels_root import (
    Effect,
    SpellLevelsRootItem,
)

from src.core.engine.contexts import AttackContext
from src.core.engine.fights.attack.models import AttackWeights, EnemyData
from src.core.engine.fights.damage_calculator import DamageCalculator
from src.core.engine.fights.effect import (
    get_effect_shield_level_bonus,
    get_life_point_percent_malus,
    get_type_effect,
)
from src.core.engine.fights.spell_modifier import SpellModifiers

LIFE_STEAL_PATTERN = re.compile(r"\bvol\b", re.IGNORECASE)


def calculate_attack_weight(
    damage_calculator: DamageCalculator,
    context: AttackContext,
    impact_mps: set[MapPoint],
    spell_lvl: SpellLevelsRootItem,
    effect: Effect,
    target_mp: MapPoint,
    enemies_data: list[EnemyData],
    modifiers: SpellModifiers,
) -> float:
    data_effect = DataReader().effect_by_id[effect.effectId]
    description_effect = I18N().name_by_id[data_effect.descriptionId]

    dmg_weight, effective_damage = calculate_damage_weight(
        damage_calculator, context, effect, target_mp, impact_mps, enemies_data
    )

    life_malus, shield_bonus = calculate_life_modifiers(context, spell_lvl)
    life_stolen = (
        effective_damage * AttackWeights.LIFE_STEAL_RATIO
        if is_life_steal(description_effect)
        else 0.0
    )

    life_recovery_weight = calculate_life_recovery_weight(
        context, life_stolen, life_malus, shield_bonus
    )

    return (dmg_weight * life_recovery_weight) / modifiers.ap_cost


@cache
def is_life_steal(description_effect: str) -> bool:
    return bool(LIFE_STEAL_PATTERN.search(description_effect))


def calculate_life_modifiers(
    context: AttackContext, spell_lvl: SpellLevelsRootItem
) -> tuple[int, int]:
    life_point_malus = 0
    shield_bonus = 0

    for effect in spell_lvl.effects:
        type_effect = get_type_effect(spell_lvl.spellId, effect)
        if type_effect is None:
            continue

        if type_effect == TypeEffect.MALUS_LIFE_PERCENT:
            life_point_malus += get_life_point_percent_malus(context.life_point, effect)
        elif type_effect == TypeEffect.SHIELD_PERCENT_LEVEL:
            shield_bonus += get_effect_shield_level_bonus(context.player_level, effect)

    return life_point_malus, shield_bonus


def calculate_life_recovery_weight(
    context: AttackContext,
    life_stolen: float,
    life_malus: int,
    shield_bonus: int,
) -> float:
    new_life = context.life_point + life_stolen - life_malus + shield_bonus
    new_life_percentage = min(new_life / context.max_life_point, 1.0)

    return 1 + (
        (new_life_percentage - context.life_percentage)
        * AttackWeights.LIFE_RECOVERY_MULTIPLIER
    )


def calculate_damage_weight(
    damage_calculator: DamageCalculator,
    context: AttackContext,
    effect: Effect,
    target_mp: MapPoint,
    impact_mps: set[MapPoint],
    enemies_data: list[EnemyData],
) -> tuple[float, float]:
    enemy_killed = 0.0
    enemy_dmg_weight = 0.0
    total_effective_damage = 0.0

    for enemy_data in enemies_data:
        if enemy_data.map_point not in impact_mps:
            continue

        distance = target_mp.distance_to_map_point(enemy_data.map_point)
        applied_steps = min(distance, effect.zoneDescr.maxDamageDecreaseApplyCount)
        damage_decrease = (
            effect.zoneDescr.damageDecreaseStepPercent * applied_steps / 100.0
        )

        damage = max(
            damage_calculator.get_damage_effect(
                effect, enemy_data.monster_grade, context.characteristic_by_id
            )
            * (1 - damage_decrease),
            0,
        )

        effective_damage = min(damage, enemy_data.life_point)
        total_effective_damage += effective_damage

        if damage >= enemy_data.life_point:
            enemy_killed += (
                AttackWeights.SUMMONED_KILL_BONUS
                if enemy_data.is_summoned
                else AttackWeights.ENEMY_KILL_BONUS
            )

        enemy_health_percentage = enemy_data.life_point / enemy_data.max_life_point
        damage_efficiency = effective_damage / enemy_health_percentage
        if enemy_data.is_summoned:
            damage_efficiency /= AttackWeights.SUMMONED_DAMAGE_DIVISOR

        enemy_dmg_weight += damage_efficiency

    damage_weight = enemy_dmg_weight * (1 + enemy_killed)
    return damage_weight, total_effective_damage
