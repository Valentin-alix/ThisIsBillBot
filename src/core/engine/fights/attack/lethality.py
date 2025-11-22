from src.core.engine.contexts import AttackContext
from src.core.engine.fights.attack.enemy_data import EnemyData
from src.core.engine.fights.damage_calculator import DamageCalculator
from src.core.engine.fights.spell import get_damage_spells
from src.core.engine.fights.spell_modifier import SpellModifiers


def can_finish_fight_this_turn(context: AttackContext, damage_calculator: DamageCalculator) -> bool:
    """No simulation: linear extrapolation of the best damage/AP spell vs the last enemy's HP."""
    if len(context.enemies_data) != 1:
        return len(context.enemies_data) == 0

    enemy = context.enemies_data[0]
    if enemy.life_point <= 0:
        return True

    best_damage_per_ap = _estimate_best_damage_per_ap(context, damage_calculator, enemy)
    return best_damage_per_ap * context.action_points >= enemy.life_point


def _estimate_best_damage_per_ap(
    context: AttackContext, damage_calculator: DamageCalculator, enemy: EnemyData
) -> float:
    is_melee = context.player_map_point.distance_to_map_point(enemy.map_point) == 1
    best = 0.0
    for spell_lvl, effect in get_damage_spells(context.spells, *context.primary_and_second_elem):
        modifiers = SpellModifiers.from_spell(context.range, spell_lvl, context.modifier_by_type_and_spell_id)
        if modifiers.ap_cost <= 0:
            continue
        damage = damage_calculator.get_damage_effect(
            effect,
            spell_lvl,
            enemy.monster_grade,
            context.characteristic_by_id,
            is_melee,
            context.primary_elem,
            context.modifier_by_type_and_spell_id,
        )
        best = max(best, damage / modifiers.ap_cost)
    return best
