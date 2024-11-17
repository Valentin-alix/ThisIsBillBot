from dataclasses import dataclass
from logging import Logger

from D3Database.data_center.data_reader import DataReader
from D3Database.data_center.i18n import I18N
from D3Database.data_center.map_reader import MapReader
from D3Database.enums.characteristic_enum import CharacteristicEnum
from D3Database.enums.directions import DirectionsEnum
from D3Database.enums.effect_element import EffectElement, TypeEffect
from D3Database.grid.map_point import MapPoint
from D3Database.models.datas.monsters_root import MonsterGrade
from D3Database.models.datas.spell_levels_root import Effect, SpellLevelsRootItem
from D3Mapping.d3_mapping.resources.protos.game.common_pb2 import (
    ActorPositionInformation,
    SpellModifier,
    SpellModifierType,
)
from src.core.engine.fights.damage_calculator import DamageCalculator
from src.core.engine.fights.effect import (
    get_effect_shield_level_bonus,
    get_life_point_percent_malus,
    get_type_effect,
)
from src.core.engine.fights.los_detector import LosDetector
from src.core.engine.fights.reachable_cells.fight_reachable_cells import (
    FightReachableCells,
)
from src.core.engine.fights.spell import (
    does_spell_need_taken_cell,
    does_spell_need_test_los,
    get_ap_cost_spell,
    get_damage_spells,
    get_max_range_spell,
    get_min_range_spell,
    get_possible_mp_spell,
    get_spell_max_cast_per_target,
    get_spell_max_cast_per_turn,
    is_spell_cast_in_line,
)
from src.core.engine.fights.spell_shape import SpellShapeEnum
from src.core.engine.fights.spell_zone import get_zone_mps
from src.core.engine.fights.zones.zone import Zone
from src.core.engine.monsters.monster_group import MonsterFighter
from src.core.engine.movements.map.path_finding.path_finding import Pathfinding
from src.core.states.game_state import GameState


class AttackWeights:
    LIFE_RECOVERY_MULTIPLIER = 3.0
    LIFE_RECOVERY_BONUS_WHEN_HEALING = 10.0
    SUMMONED_ENEMY_PENALTY = 0.5
    SUMMONED_DAMAGE_DIVISOR = 2
    ENEMY_KILL_BONUS = 1.0
    SUMMONED_KILL_BONUS = 0.5
    MIN_LIFE_PERCENTAGE_WEIGHT = 1.0


@dataclass
class SpellModifiers:
    ap_cost: int
    max_cast_per_turn: int
    max_cast_per_target: int
    range_min: int
    range_max: int
    cast_line: int | None

    @classmethod
    def from_spell(
        cls,
        stat_po: int,
        spell_lvl: SpellLevelsRootItem,
        modifiers_map: dict[tuple[int, SpellModifierType], SpellModifier],
    ) -> "SpellModifiers":
        spell_id = spell_lvl.spellId
        return cls(
            ap_cost=get_ap_cost_spell(
                spell_lvl, modifiers_map.get((spell_id, SpellModifierType.AP_COST))
            ),
            max_cast_per_turn=(
                get_spell_max_cast_per_turn(
                    spell_lvl,
                    modifiers_map.get((spell_id, SpellModifierType.MAX_CAST_PER_TURN)),
                )
            ),
            max_cast_per_target=(
                get_spell_max_cast_per_target(
                    spell_lvl,
                    modifiers_map.get(
                        (spell_id, SpellModifierType.MAX_CAST_PER_TARGET)
                    ),
                )
            ),
            range_min=get_min_range_spell(
                spell_lvl, modifiers_map.get((spell_id, SpellModifierType.RANGE_MIN))
            ),
            range_max=get_max_range_spell(
                stat_po,
                spell_lvl,
                modifiers_map.get((spell_id, SpellModifierType.RANGE_MAX)),
            ),
            cast_line=is_spell_cast_in_line(
                spell_lvl, modifiers_map.get((spell_id, SpellModifierType.CAST_LINE))
            ),
        )


@dataclass
class EnemyData:
    actor: ActorPositionInformation
    map_point: MapPoint
    life_point: int
    max_life_point: int
    is_summoned: bool
    monster_grade: MonsterGrade | None


@dataclass
class Attacker:
    game_state: GameState
    fight_reachable_cells: FightReachableCells
    damage_calculator: DamageCalculator
    path_finding: Pathfinding
    logger: Logger

    def _prepare_enemies_data(
        self, enemies: list[ActorPositionInformation]
    ) -> list[EnemyData]:
        enemies_data = []
        for enemy in enemies:
            enemy_mp = MapPoint.from_cell_id(enemy.disposition.cell_id)
            if enemy.actor_id in self.game_state.entity.actor_fight_by_id:
                actor_fight = self.game_state.entity.actor_fight_by_id[enemy.actor_id]
                life_point = actor_fight.life_point
                is_summoned = actor_fight.is_summoned
            else:
                life_point = 1_000
                is_summoned = False

            monster_info: MonsterFighter = (
                enemy.actor_information.fighter.ai_fighter.monster_fighter_information
            )
            monster_id = monster_info.monster_gid

            monster_grade = None
            if monster_id in DataReader().monsters_by_id:
                monster = DataReader().monsters_by_id[monster_id]
                monster_grade = monster.grades[monster_info.creature_grade - 1]
                max_life_point = monster_grade.lifePoints
            else:
                max_life_point = 100

            enemies_data.append(
                EnemyData(
                    actor=enemy,
                    map_point=enemy_mp,
                    life_point=life_point,
                    max_life_point=max_life_point,
                    is_summoned=is_summoned,
                    monster_grade=monster_grade,
                )
            )
        return enemies_data

    def _is_spell_valid_for_turn(
        self,
        spell_lvl: SpellLevelsRootItem,
        modifiers: SpellModifiers,
        rejection_stats: dict[str, int],
    ) -> bool:
        current_ap = self.game_state.fight.get_stat_by_id(
            CharacteristicEnum.ACTION_POINTS
        )

        if modifiers.ap_cost > current_ap:
            rejection_stats["insufficient_ap"] += 1
            return False

        if spell_lvl.initialCooldown != 0:
            rejection_stats["initial_cooldown"] += 1
            return False

        if spell_lvl.globalCooldown != 0:
            rejection_stats["global_cooldown"] += 1
            return False

        count_casted = (
            self.game_state.fight.count_casted_by_spell_id_on_current_turn.get(
                spell_lvl.spellId
            )
        )
        if (
            count_casted is not None
            and modifiers.max_cast_per_turn != 0
            and modifiers.max_cast_per_turn <= count_casted
        ):
            rejection_stats["max_cast_per_turn"] += 1
            return False

        return True

    def get_valid_spells_for_turn(
        self,
    ) -> list[tuple[SpellLevelsRootItem, Effect, SpellModifiers]]:
        valuable_spells = get_damage_spells(
            self.game_state.fight.spells, EffectElement.CHANCE, EffectElement.CHANCE
        )

        rejection_stats = {
            "insufficient_ap": 0,
            "initial_cooldown": 0,
            "global_cooldown": 0,
            "max_cast_per_turn": 0,
        }

        valid_spell_levels: list[
            tuple[SpellLevelsRootItem, Effect, SpellModifiers]
        ] = []
        modifiers_map = self.game_state.fight.modifier_by_type_and_spell_id

        for spell_lvl, effect in valuable_spells:
            modifiers = SpellModifiers.from_spell(
                self.game_state.fight.get_stat_by_id(CharacteristicEnum.RANGE),
                spell_lvl,
                modifiers_map,
            )
            if self._is_spell_valid_for_turn(spell_lvl, modifiers, rejection_stats):
                valid_spell_levels.append((spell_lvl, effect, modifiers))

        total_rejected = sum(rejection_stats.values())
        if total_rejected > 0:
            stats_str = ", ".join(
                f"{k}: {v}" for k, v in rejection_stats.items() if v > 0
            )
            self.logger.info(
                f"Spell validation: {len(valid_spell_levels)}/{len(valuable_spells)} valid "
                f"(AP: {self.game_state.fight.get_stat_by_id(CharacteristicEnum.ACTION_POINTS)}) - Rejected: {stats_str}"
            )
        else:
            self.logger.info(
                f"Spell validation: {len(valid_spell_levels)}/{len(valuable_spells)} valid "
                f"(AP: {self.game_state.fight.get_stat_by_id(CharacteristicEnum.ACTION_POINTS)})"
            )

        return valid_spell_levels

    def find_best_attack_from_mp(
        self,
    ) -> tuple[MapPoint, SpellLevelsRootItem, MapPoint] | None:
        entities_id_by_mp: dict[MapPoint, int] = {
            MapPoint.from_cell_id(actor.disposition.cell_id): actor.actor_id
            for actor in self.game_state.entity.actor_by_id.values()
            if actor.disposition.cell_id != -1
        }
        entities_mp = set(entities_id_by_mp.keys())
        enemies = self.game_state.fight.get_enemies(self.game_state.player.character_id)
        enemies_mp = {
            MapPoint.from_cell_id(enemy.disposition.cell_id) for enemy in enemies
        }
        enemies_data = self._prepare_enemies_data(enemies)

        movable_mps = self.fight_reachable_cells.search(
            enemies_mp=enemies_mp, entities_mp=entities_mp
        )
        movable_mps[self.game_state.map.map_point] = (
            self.game_state.fight.get_stat_by_id(CharacteristicEnum.MOVEMENT_POINTS)
        )

        valid_spells_for_turn = self.get_valid_spells_for_turn()
        if not valid_spells_for_turn:
            self.logger.warning("No valid spells available for this turn")
            return None

        modifiers_map = self.game_state.fight.modifier_by_type_and_spell_id
        player_range = self.game_state.fight.get_stat_by_id(CharacteristicEnum.RANGE)

        best_attack: (
            tuple[float, int, MapPoint, SpellLevelsRootItem, MapPoint] | None
        ) = None
        total_candidates = 0
        cast_rejection_stats = {
            "cell_not_walkable": 0,
            "max_cast_per_target": 0,
            "no_los": 0,
        }
        spells_without_targets = 0

        zone_spell_cache: dict[
            tuple[SpellShapeEnum, int, int, MapPoint, bool], Zone
        ] = {}
        weight_cache: dict[
            tuple[SpellLevelsRootItem, DirectionsEnum, MapPoint], float
        ] = {}

        for spell_lvl, effect, modifiers in valid_spells_for_turn:
            zone_shape = SpellShapeEnum(effect.zoneDescr.shape)
            zone_size = effect.zoneDescr.param1
            zone_alt_size = effect.zoneDescr.param2
            stop_at_target = bool(effect.zoneDescr.isStopAtTarget)
            needs_taken_cell = does_spell_need_taken_cell(spell_lvl) or zone_size == 0

            spell_id = spell_lvl.spellId
            modifier_range_min = modifiers_map.get((spell_id, SpellModifierType.RANGE_MIN))
            modifier_range_max = modifiers_map.get((spell_id, SpellModifierType.RANGE_MAX))
            modifier_cast_line = modifiers_map.get((spell_id, SpellModifierType.CAST_LINE))

            spell_has_targets = False

            for movable_mp, remaining_pm in movable_mps.items():
                cache_key = (
                    zone_shape,
                    zone_size,
                    zone_alt_size,
                    movable_mp,
                    stop_at_target,
                )
                if cache_key not in zone_spell_cache:
                    zone_spell_cache[cache_key] = get_zone_mps(
                        shape=zone_shape,
                        alternative_size=zone_alt_size,
                        size=zone_size,
                        caster_mp=movable_mp,
                        stop_at_target=stop_at_target,
                    )
                zone_spell = zone_spell_cache[cache_key]

                targetable_mps = get_possible_mp_spell(
                    movable_mp,
                    spell_lvl,
                    player_range,
                    modifier_range_min=modifier_range_min,
                    modifier_range_max=modifier_range_max,
                    modifier_cast_line=modifier_cast_line,
                )

                if needs_taken_cell:
                    targetable_mps &= entities_mp
                else:
                    targetable_mps = {
                        mp
                        for enemy_mp in enemies_mp
                        for mp in zone_spell.get_mps(
                            enemy_mp, enemy_mp.orientation_to(movable_mp)
                        )
                        if mp in targetable_mps
                    }

                for targetable_mp in targetable_mps:
                    cast_result = self._can_cast_spell_on_mp(
                        movable_mp,
                        spell_lvl,
                        targetable_mp,
                        modifiers,
                        entities_mp,
                        entities_id_by_mp,
                        cast_rejection_stats,
                    )
                    if not cast_result:
                        continue

                    direction = movable_mp.orientation_to(targetable_mp)
                    weight_cache_key = (spell_lvl, direction, targetable_mp)

                    if weight_cache_key not in weight_cache:
                        impact_mps = zone_spell.get_mps(
                            mp=targetable_mp, direction=direction
                        )
                        weight_cache[weight_cache_key] = self._calculate_attack_weight(
                            impact_mps,
                            spell_lvl,
                            effect,
                            targetable_mp,
                            enemies_data,
                            modifiers,
                        )

                    total_weight = weight_cache[weight_cache_key]
                    spell_has_targets = True
                    total_candidates += 1

                    if best_attack is None or self._is_better_attack(
                        total_weight,
                        remaining_pm,
                        movable_mp,
                        targetable_mp,
                        best_attack,
                    ):
                        best_attack = (
                            total_weight,
                            remaining_pm,
                            movable_mp,
                            spell_lvl,
                            targetable_mp,
                        )

            if not spell_has_targets:
                spells_without_targets += 1

        if best_attack is not None and best_attack[0] > 0:
            best_spell_name = I18N().name_by_id[
                DataReader().spell_by_id[best_attack[3].spellId].nameId
            ]
            self.logger.info(
                f"Attack found: {best_spell_name} (weight: {best_attack[0]:.2f}, {total_candidates} targets evaluated)"
            )
            return best_attack[2], best_attack[3], best_attack[4]

        rejection_parts = []
        if spells_without_targets > 0:
            rejection_parts.append(f"{spells_without_targets} spells without targets")

        total_cast_rejections = sum(cast_rejection_stats.values())
        if total_cast_rejections > 0:
            cast_stats = ", ".join(
                f"{k}: {v}" for k, v in cast_rejection_stats.items() if v > 0
            )
            rejection_parts.append(f"Cast rejections ({cast_stats})")

        if rejection_parts:
            self.logger.warning(f"No attack found - {'; '.join(rejection_parts)}")
        else:
            self.logger.warning("No attack found - no targets evaluated")

        return None

    def _is_better_attack(
        self,
        weight: float,
        remaining_pm: int,
        from_mp: MapPoint,
        target_mp: MapPoint,
        current_best: tuple[float, int, MapPoint, SpellLevelsRootItem, MapPoint],
    ) -> bool:
        if weight < current_best[0]:
            return False

        if weight > current_best[0]:
            return True

        if remaining_pm < current_best[1]:
            return False

        if remaining_pm > current_best[1]:
            return True

        current_distance = current_best[4].distance_to_map_point(current_best[2])
        new_distance = target_mp.distance_to_map_point(from_mp)
        return new_distance > current_distance

    def _can_cast_spell_on_mp(
        self,
        from_mp: MapPoint,
        spell_lvl: SpellLevelsRootItem,
        mp: MapPoint,
        modifiers: SpellModifiers,
        entities_mp: set[MapPoint],
        entities_id_by_mp: dict[MapPoint, int],
        rejection_stats: dict[str, int],
    ) -> bool:
        targetable_mp_data = MapReader().get_cell_data_by_cell_id(
            self.game_state.map.map_id, mp.cell_id
        )
        if not targetable_mp_data.mov or not targetable_mp_data.los:
            rejection_stats["cell_not_walkable"] += 1
            return False

        count_casted = (
            self.game_state.fight.count_casted_by_spell_id_on_current_turn.get(
                spell_lvl.spellId
            )
        )
        entity_id = entities_id_by_mp.get(mp)
        if (
            count_casted is not None
            and entity_id is not None
            and modifiers.max_cast_per_target != 0
            and modifiers.max_cast_per_target <= count_casted
        ):
            rejection_stats["max_cast_per_target"] += 1
            return False

        if does_spell_need_test_los(spell_lvl) and not LosDetector.los_between(
            map_id=self.game_state.map.map_id,
            taken_mps=entities_mp,
            start=from_mp,
            end=mp,
        ):
            rejection_stats["no_los"] += 1
            return False

        return True

    def _calculate_life_modifiers(
        self, spell_lvl: SpellLevelsRootItem
    ) -> tuple[int, int]:
        life_point_malus = 0
        shield_bonus = 0

        for effect in spell_lvl.effects:
            type_effect = get_type_effect(spell_lvl.spellId, effect)
            if type_effect is None:
                continue

            if type_effect == TypeEffect.MALUS_LIFE_PERCENT and life_point_malus == 0:
                life_point_malus = get_life_point_percent_malus(
                    self.game_state.fight.life_point, effect
                )
            elif type_effect == TypeEffect.SHIELD_PERCENT_LEVEL and shield_bonus == 0:
                shield_bonus = get_effect_shield_level_bonus(
                    self.game_state.player.level, effect
                )

        return life_point_malus, shield_bonus

    def _calculate_life_recovery_weight(
        self, life_stolen: float, life_malus: int, shield_bonus: int
    ) -> float:
        new_life = (
            self.game_state.fight.life_point + life_stolen - life_malus + shield_bonus
        )
        new_life_percentage = min(new_life / self.game_state.fight.max_life_point, 1.0)

        life_gain_percentage = (
            new_life_percentage - self.game_state.fight.life_percentage
        ) * AttackWeights.LIFE_RECOVERY_MULTIPLIER

        if life_stolen > 0 or shield_bonus > 0:
            return AttackWeights.LIFE_RECOVERY_BONUS_WHEN_HEALING

        if self.game_state.fight.life_percentage > 0:
            life_gain_percentage /= self.game_state.fight.life_percentage

        return max(life_gain_percentage, AttackWeights.MIN_LIFE_PERCENTAGE_WEIGHT)

    def _calculate_attack_weight(
        self,
        impact_mps: set[MapPoint],
        spell_lvl: SpellLevelsRootItem,
        effect: Effect,
        target_mp: MapPoint,
        enemies_data: list[EnemyData],
        modifiers: SpellModifiers,
    ) -> float:
        data_effect = DataReader().effect_by_id[effect.effectId]
        description_effect = I18N().name_by_id[data_effect.descriptionId]
        is_life_steal = "vol" in description_effect

        dmg_weight, total_damage = self._calculate_damage_weight(
            effect, target_mp, impact_mps, enemies_data
        )

        life_stolen = total_damage if is_life_steal else 0.0
        life_malus, shield_bonus = self._calculate_life_modifiers(spell_lvl)

        if life_malus > 0:
            dmg_weight /= 1 + (life_malus / max(self.game_state.fight.life_point, 1))

        life_recovery_weight = self._calculate_life_recovery_weight(
            life_stolen, life_malus, shield_bonus
        )

        return (dmg_weight * (1 + life_recovery_weight)) / modifiers.ap_cost

    def _calculate_damage_weight(
        self,
        effect: Effect,
        target_mp: MapPoint,
        impact_mps: set[MapPoint],
        enemies_data: list[EnemyData],
    ) -> tuple[float, float]:
        enemy_killed = 0.0
        enemy_dmg_weight = 0.0
        total_damage = 0.0

        impact_mps_set = set(impact_mps)

        for enemy_data in enemies_data:
            if enemy_data.map_point not in impact_mps_set:
                continue

            distance = target_mp.distance_to_map_point(enemy_data.map_point)
            damage_decrease = (
                min(
                    effect.zoneDescr.damageDecreaseStepPercent * distance,
                    effect.zoneDescr.maxDamageDecreaseApplyCount,
                )
                / 100.0
            )

            damage = self.damage_calculator.get_damage_effect(
                effect, enemy_data.monster_grade
            ) * (1 - damage_decrease)

            total_damage += damage

            if enemy_data.life_point - damage <= 0:
                enemy_killed += (
                    AttackWeights.SUMMONED_KILL_BONUS
                    if enemy_data.is_summoned
                    else AttackWeights.ENEMY_KILL_BONUS
                )

            normalized_health = enemy_data.life_point / max(
                enemy_data.max_life_point, 1
            )
            damage_efficiency = damage / normalized_health
            if enemy_data.is_summoned:
                damage_efficiency /= AttackWeights.SUMMONED_DAMAGE_DIVISOR

            enemy_dmg_weight += damage_efficiency

        damage_weight = enemy_dmg_weight * (1 + enemy_killed)
        return damage_weight, total_damage
