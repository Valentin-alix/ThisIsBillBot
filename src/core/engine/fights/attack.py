from dataclasses import dataclass
from logging import Logger
from typing import Iterable

from D3Database.data_center.data_reader import DataReader
from D3Database.data_center.i18n import I18N
from D3Database.data_center.map_reader import MapReader
from D3Database.enums.characteristic_enum import CharacteristicEnum
from D3Database.enums.directions import DirectionsEnum
from D3Database.enums.effect_element import EffectElement, TypeEffect
from D3Database.grid.map_point import MapPoint
from D3Database.models.datas.spell_levels_root import Effect, SpellLevelsRootItem
from D3Mapping.d3_mapping.resources.protos.game.common_pb2 import (
    ActorPositionInformation,
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
    get_possible_mp_spell,
    get_spell_max_cast_per_target,
    get_spell_max_cast_per_turn,
)
from src.core.engine.fights.spell_shape import SpellShapeEnum
from src.core.engine.fights.spell_zone import get_zone_mps
from src.core.engine.monsters.monster_group import MonsterFighter
from src.core.engine.movements.map.path_finding.path_finding import Pathfinding
from src.core.states.game_state import GameState


@dataclass
class Attacker:
    game_state: GameState
    fight_reachable_cells: FightReachableCells
    damage_calculator: DamageCalculator
    path_finding: Pathfinding
    logger: Logger

    def get_valid_spells_for_turn(self) -> list[tuple[SpellLevelsRootItem, Effect]]:
        self.logger.info(f"Count spell : {len(self.game_state.fight.spells)}")
        valuable_spells = get_damage_spells(
            self.game_state.fight.spells, EffectElement.CHANCE, EffectElement.CHANCE
        )
        self.logger.info(f"Count valuable spell : {len(valuable_spells)}")
        self.logger.info(
            f"PA : {
                self.game_state.fight.get_stat_by_id(CharacteristicEnum.ACTION_POINTS)
            }"
        )
        valid_spell_levels: list[tuple[SpellLevelsRootItem, Effect]] = []
        for spell_lvl, effect in valuable_spells:
            spell_ap_cost = get_ap_cost_spell(
                spell_lvl,
                self.game_state.fight.modifier_by_type_and_spell_id.get(
                    (spell_lvl.spellId, SpellModifierType.AP_COST)
                ),
            )
            if spell_ap_cost > self.game_state.fight.get_stat_by_id(
                CharacteristicEnum.ACTION_POINTS
            ):
                continue
            if spell_lvl.initialCooldown != 0:
                continue

            if spell_lvl.globalCooldown != 0:
                continue

            max_cast_per_turn = get_spell_max_cast_per_turn(
                spell_lvl,
                self.game_state.fight.modifier_by_type_and_spell_id.get(
                    (spell_lvl.spellId, SpellModifierType.MAX_CAST_PER_TURN)
                ),
            )
            count_casted = (
                self.game_state.fight.count_casted_by_spell_id_on_current_turn.get(
                    spell_lvl.spellId
                )
            )
            if (
                count_casted is not None
                and max_cast_per_turn != 0
                and max_cast_per_turn <= count_casted
            ):
                self.logger.info(
                    f"Spell {I18N().name_by_id[DataReader().spell_by_id[spell_lvl.spellId].nameId]} reached max cast per turn : {count_casted}"
                )
                continue
            valid_spell_levels.append((spell_lvl, effect))
        return valid_spell_levels

    def find_best_attack_from_mp(
        self,
    ) -> tuple[MapPoint, SpellLevelsRootItem, MapPoint] | None:
        """get the attack that do the most damage with less ap"""
        best_attack: (
            tuple[float, int, MapPoint, SpellLevelsRootItem, MapPoint] | None
        ) = None
        entities_id_by_mp: dict[MapPoint, int] = {
            MapPoint.from_cell_id(actor.disposition.cell_id): actor.actor_id
            for actor in self.game_state.entity.actor_by_id.values()
            if actor.disposition.cell_id != -1
        }
        entities_mp = set(entities_id_by_mp)
        enemies = self.game_state.fight.get_enemies(self.game_state.player.character_id)
        enemies_mp = {
            MapPoint.from_cell_id(enemy.disposition.cell_id) for enemy in enemies
        }
        movable_mps = self.fight_reachable_cells.search(
            enemies_mp=enemies_mp, entities_mp=entities_mp
        )
        movable_mps[self.game_state.map.map_point] = (
            self.game_state.fight.get_stat_by_id(CharacteristicEnum.MOVEMENT_POINTS)
        )

        self.logger.info(
            f"find from mp {self.game_state.map.map_point} with entities {entities_id_by_mp} and enemies "
            f"mp : {enemies_mp}"
        )
        valid_spells_for_turn = self.get_valid_spells_for_turn()

        self.logger.info(f"Count valid spell for turn : {len(valid_spells_for_turn)}")
        for spell_lvl, effect in valid_spells_for_turn:
            weight_by_direction_and_target: dict[
                tuple[DirectionsEnum, MapPoint], float
            ] = {}
            for movable_mp, remaining_pm in movable_mps.items():
                targetable_mps = get_possible_mp_spell(
                    movable_mp,
                    spell_lvl,
                    self.game_state.fight.get_stat_by_id(CharacteristicEnum.RANGE),
                    modifier_range_min=self.game_state.fight.modifier_by_type_and_spell_id.get(
                        (spell_lvl.spellId, SpellModifierType.RANGE_MIN)
                    ),
                    modifier_range_max=self.game_state.fight.modifier_by_type_and_spell_id.get(
                        (spell_lvl.spellId, SpellModifierType.RANGE_MAX)
                    ),
                    modifier_cast_line=self.game_state.fight.modifier_by_type_and_spell_id.get(
                        (spell_lvl.spellId, SpellModifierType.CAST_LINE)
                    ),
                )

                zone_spell = get_zone_mps(
                    shape=SpellShapeEnum(effect.zoneDescr.shape),
                    alternative_size=effect.zoneDescr.param2,
                    size=effect.zoneDescr.param1,
                    caster_mp=movable_mp,
                    stop_at_target=bool(effect.zoneDescr.isStopAtTarget),
                )
                if (
                    does_spell_need_taken_cell(spell_lvl)
                    or effect.zoneDescr.param1 == 0
                ):
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
                    if not self.can_cast_spell_on_mp(
                        movable_mp,
                        spell_lvl,
                        targetable_mp,
                        entities_mp,
                        entities_id_by_mp,
                    ):
                        continue
                    direction = movable_mp.orientation_to(targetable_mp)
                    if (direction, targetable_mp) in weight_by_direction_and_target:
                        total_weight_spell = weight_by_direction_and_target[
                            (direction, targetable_mp)
                        ]
                    else:
                        impact_mps = zone_spell.get_mps(
                            mp=targetable_mp, direction=direction
                        )
                        total_weight_spell = self.get_weight_attack(
                            impact_mps, spell_lvl, effect, targetable_mp, enemies
                        )
                        self.logger.info(
                            f"Found total weight {total_weight_spell} on mp {targetable_mp.cell_id} with spell {I18N().name_by_id[DataReader().spell_by_id[spell_lvl.spellId].nameId]}"
                        )
                        weight_by_direction_and_target[(direction, targetable_mp)] = (
                            total_weight_spell
                        )

                    if best_attack is not None and total_weight_spell < best_attack[0]:
                        continue

                    if best_attack is not None and best_attack[0] == total_weight_spell:
                        if remaining_pm < best_attack[1] or (
                            remaining_pm == best_attack[1]
                            and targetable_mp.distance_to_map_point(movable_mp)
                            >= best_attack[4].distance_to_map_point(best_attack[2])
                        ):
                            # same weight but the other need less pm or is farther
                            continue

                    best_attack = (
                        total_weight_spell,
                        remaining_pm,
                        movable_mp,
                        spell_lvl,
                        targetable_mp,
                    )

        if best_attack is not None and best_attack[0] > 0:
            name_spell = I18N().name_by_id[
                DataReader().spell_by_id[best_attack[3].spellId].nameId
            ]
            self.logger.info(
                f"Found best attack with weight : {best_attack[0]} for spell {name_spell} at target {best_attack[4]}"
            )
            return best_attack[2], best_attack[3], best_attack[4]
        else:
            self.logger.info("Did not found any attack")
        return None

    def can_cast_spell_on_mp(
        self,
        from_mp: MapPoint,
        spell_lvl: SpellLevelsRootItem,
        mp: MapPoint,
        entities_mp: Iterable[MapPoint],
        entities_id_by_mp: dict[MapPoint, int],
    ):
        targetable_mp_data = MapReader().get_cell_data_by_cell_id(
            self.game_state.map.map_id, mp.cell_id
        )
        if not targetable_mp_data.mov or not targetable_mp_data.los:
            return False

        max_cast_per_target = get_spell_max_cast_per_target(
            spell_lvl,
            self.game_state.fight.modifier_by_type_and_spell_id.get(
                (
                    spell_lvl.spellId,
                    SpellModifierType.MAX_CAST_PER_TARGET,
                )
            ),
        )
        count_casted = (
            self.game_state.fight.count_casted_by_spell_id_on_current_turn.get(
                spell_lvl.spellId
            )
        )
        entity_id = entities_id_by_mp.get(mp)
        if (
            count_casted is not None
            and entity_id is not None
            and max_cast_per_target != 0
            and max_cast_per_target <= count_casted
        ):
            return False

        if does_spell_need_test_los(spell_lvl) and not LosDetector.los_between(
            map_id=self.game_state.map.map_id,
            taken_mps=entities_mp,
            start=from_mp,
            end=mp,
        ):
            return False

        return True

    def get_weight_attack(
        self,
        impact_mps: Iterable[MapPoint],
        spell_lvl: SpellLevelsRootItem,
        effect: Effect,
        target_mp: MapPoint,
        enemies: list[ActorPositionInformation],
    ) -> float:
        spell_ap_cost = get_ap_cost_spell(
            spell_lvl,
            self.game_state.fight.modifier_by_type_and_spell_id.get(
                (spell_lvl.spellId, SpellModifierType.AP_COST)
            ),
        )

        data_effect = DataReader().effect_by_id[effect.effectId]
        description_effect = I18N().name_by_id[data_effect.descriptionId]

        dmg_weight_spell, thieft_life = self.get_weight_dmg_and_life_thieft_effect(
            effect, target_mp, impact_mps, enemies, description_effect
        )
        self.logger.info(
            f"Dmg weight spell : {dmg_weight_spell} thieft life {thieft_life}"
        )

        life_point_malus: int = 0
        shield_bonus: int = 0
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
        dmg_weight_spell /= 1 + (
            life_point_malus / max(self.game_state.fight.life_point, 1)
        )

        self.logger.info(
            f"Dmg weight spell after life point malus : {dmg_weight_spell}"
        )

        # ici on récupère le life percentage qu'on pourrait gagné avec le spell
        life_percentage_weight: float = (
            min(
                (
                    self.game_state.fight.life_point
                    + thieft_life
                    - life_point_malus
                    + shield_bonus
                )
                / self.game_state.fight.max_life_point,
                1,
            )
            - self.game_state.fight.life_percentage
        ) * 3

        self.logger.info(
            f"Life weight before divide: {life_percentage_weight}\n\
                    Life point malus : {life_point_malus}\n\
                    Shield bonus : {shield_bonus}\n\
                    Thieft_life : {thieft_life}\n\
                    Life percentage : {self.game_state.fight.life_percentage}\n"
        )

        # puis on divise par le life percentage actuel (parce qu'on veux recup des pdv quand on est low)
        life_percentage_weight /= self.game_state.fight.life_percentage

        # <!> Warning custom percentage weight bc life point is not all time good
        if thieft_life > 0 or shield_bonus > 0:
            life_percentage_weight = 10

        if life_percentage_weight < 0:
            self.logger.error(
                f"Invalid life percentage weight : {life_percentage_weight}\n\
                    Life point malus : {life_point_malus}\n\
                    Shield bonus : {shield_bonus}\n\
                    Life percentage : {self.game_state.fight.life_percentage}\n\
                    Life point : {self.game_state.fight.life_point}\n\
                    Max life point {self.game_state.fight.max_life_point}"
            )
            life_percentage_weight = 1

        self.logger.info(f"life percentage weight : {life_percentage_weight}")

        return (dmg_weight_spell * (1 + life_percentage_weight)) / spell_ap_cost

    def get_weight_dmg_and_life_thieft_effect(
        self,
        effect: Effect,
        target_mp: MapPoint,
        impact_mps: Iterable[MapPoint],
        enemies: list[ActorPositionInformation],
        description_effect: str,
    ) -> tuple[float, float]:
        enemy_killed: float = 0
        enemy_dmg_weight: float = 0
        enemy_total_dmg: float = 0
        for enemy in enemies:
            enemy_mp = MapPoint.from_cell_id(enemy.disposition.cell_id)
            if enemy_mp not in impact_mps:
                continue
            if enemy.actor_id in self.game_state.entity.actor_fight_by_id:
                actor_fight = self.game_state.entity.actor_fight_by_id[enemy.actor_id]
                life_point = actor_fight.life_point
                is_summoned = actor_fight.is_summoned
            else:
                life_point = 1_000
                is_summoned = False

            # if not is_included_by_mask(
            #     caster_id=self.game_state.player.character_id,
            #     caster_team=Team.TEAM_DEFENDER,
            #     masks=effect.targetMask.split(","),
            #     target_actor=enemy,
            # ):
            #     self.logger.info(
            #         f"effect with mask {effect.targetMask} not included for enemy {enemy.actor_id}"
            #     )
            #     continue
            monster_info: MonsterFighter = (
                enemy.actor_information.fighter.ai_fighter.monster_fighter_information
            )
            monster_id, monster_grade = (
                monster_info.monster_gid,
                monster_info.creature_grade,
            )
            if monster_id in DataReader().monsters_by_id:
                monster = DataReader().monsters_by_id[monster_id]
                monster_grade = monster.grades[monster_grade - 1]
                monster_life_point = monster_grade.lifePoints
            else:
                self.logger.error(f"Did not found monster {monster_id}")
                monster_grade = None
                monster_life_point = 100

            decrease_by_dist_percent = (
                min(
                    effect.zoneDescr.damageDecreaseStepPercent
                    * target_mp.distance_to_map_point(enemy_mp),
                    effect.zoneDescr.maxDamageDecreaseApplyCount,
                )
                / 100
            )
            dmg: float = self.damage_calculator.get_damage_effect(
                effect, monster_grade
            ) * (1 - decrease_by_dist_percent)
            enemy_total_dmg += dmg
            if life_point - dmg <= 0:
                enemy_killed += 0.5 if is_summoned else 1
            enemy_dmg_weight += (dmg / (life_point / max(monster_life_point, 1))) / (
                2 if is_summoned else 1
            )

        dmg_weight = (enemy_dmg_weight) * (1 + enemy_killed)

        if "vol" in description_effect:
            thieft_life: float = enemy_total_dmg
        else:
            thieft_life = 0

        return dmg_weight, thieft_life
