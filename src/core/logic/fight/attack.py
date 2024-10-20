from dataclasses import dataclass
from logging import Logger
from typing import Iterable

from d3_mapping.resources.protos.game.common_pb2 import (
    ActorPositionInformation,
    SpellModifierType,
    Team,
)
from data_center.data_reader import DataReader
from data_center.i18n import I18N
from data_center.map_reader import MapReader
from grid.directions import DirectionsEnum
from grid.map_point import MapPoint
from models.datas.spell_levels_root import Effect, SpellLevelsRootItem

from src.core.logic.fight.damage_calculator import DamageCalculator
from src.core.logic.fight.effect import (
    get_type_effect,
    is_included_by_mask,
)
from src.core.logic.fight.los_detector import LosDetector
from src.core.logic.fight.reachable_cells.fight_reachable_cells import (
    FightReachableCells,
)
from src.core.logic.fight.spell import (
    does_spell_need_taken_cell,
    does_spell_need_test_los,
    get_ap_cost_spell,
    get_damage_spells,
    get_possible_mp_spell,
    get_spell_max_cast_per_target,
    get_spell_max_cast_per_turn,
)
from src.core.logic.fight.spell_zone import get_zone_mps
from src.core.logic.grid.path_finding.path_finding import Pathfinding
from src.core.states.game_state import GameState
from src.interfaces.enums.characteristic_enum import CharacteristicEnum
from src.interfaces.enums.effect_element import TypeEffect
from src.interfaces.enums.spell_shape_enum import SpellShapeEnum


@dataclass
class Attacker:
    game_state: GameState
    fight_reachable_cells: FightReachableCells
    damage_calculator: DamageCalculator
    path_finding: Pathfinding
    logger: Logger

    def get_valid_spells_for_turn(self) -> list[tuple[SpellLevelsRootItem, Effect]]:
        valuable_spells = get_damage_spells(
            self.game_state.fight.spells,
            *self.game_state.fight.primary_and_second_elem,
        )
        self.logger.info(
            f"PA : {
                self.game_state.player.get_player_stat_by_id(
                    CharacteristicEnum.ACTION_POINTS
                )
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
            if spell_ap_cost > self.game_state.player.get_player_stat_by_id(
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
            count_casted = self.game_state.fight.count_casted_by_spell_id.get(
                spell_lvl.spellId
            )
            if (
                count_casted is not None
                and max_cast_per_turn != 0
                and max_cast_per_turn <= count_casted
            ):
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
        enemies = self.game_state.entity.get_enemies(
            self.game_state.player.character_id
        )
        enemies_mp = {
            MapPoint.from_cell_id(enemy.disposition.cell_id) for enemy in enemies
        }
        movable_mps = self.fight_reachable_cells.search(
            enemies_mp=enemies_mp, entities_mp=entities_mp
        )
        movable_mps[self.game_state.player.map_point] = (
            self.game_state.player.get_player_stat_by_id(
                CharacteristicEnum.MOVEMENT_POINTS
            )
        )

        self.logger.info(
            f"find from mp {self.game_state.player.map_point} with entities {entities_id_by_mp} and enemies "
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
                    self.game_state.player.get_player_stat_by_id(
                        CharacteristicEnum.RANGE
                    ),
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
                        weight_by_direction_and_target[(direction, targetable_mp)] = (
                            total_weight_spell
                        )

                    if best_attack is not None and total_weight_spell < best_attack[0]:
                        continue

                    if best_attack is not None and best_attack[0] == total_weight_spell:
                        if remaining_pm <= best_attack[1]:
                            # same weight but the other need less pm
                            continue

                    best_attack = (
                        total_weight_spell,
                        remaining_pm,
                        movable_mp,
                        spell_lvl,
                        targetable_mp,
                    )

        if best_attack is not None and best_attack[0] > 0:
            name_spell = I18N.name_by_id[
                DataReader().spell_by_id[best_attack[3].spellId].nameId
            ]
            self.logger.info(
                f"Found best attack with weight : {best_attack[0]} for spell {name_spell} at target {best_attack[4]}"
            )
            return best_attack[2], best_attack[3], best_attack[4]
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
        count_casted = self.game_state.fight.count_casted_by_spell_id.get(
            spell_lvl.spellId
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
        description_effect = I18N.name_by_id[data_effect.descriptionId]

        dmg_weight_spell, _ = self.get_weight_dmg_and_life_thieft_effect(
            effect, target_mp, impact_mps, enemies, description_effect
        )
        do_life_point_malus: bool = False
        does_shield: bool = False
        does_thieft_life: bool = "vol" in description_effect
        for effect in spell_lvl.effects:
            type_effect = get_type_effect(spell_lvl.spellId, effect)
            if type_effect is None:
                continue
            if (
                type_effect == TypeEffect.MALUS_LIFE_PERCENT
                and do_life_point_malus == 0
            ):
                do_life_point_malus = True
            elif type_effect == TypeEffect.SHIELD_PERCENT_LEVEL and does_shield == 0:
                does_shield = True

        malus = 1
        if do_life_point_malus:
            malus += 1

        bonus = 1
        if does_shield:
            bonus += 1
        if does_thieft_life:
            bonus += 1

        dmg_weight_spell *= (bonus) / malus

        return dmg_weight_spell / spell_ap_cost

    def get_weight_dmg_and_life_thieft_effect(
        self,
        effect: Effect,
        target_mp: MapPoint,
        impact_mps: Iterable[MapPoint],
        enemies: list[ActorPositionInformation],
        description_effect: str,
    ) -> tuple[float, float]:
        enemy_total_dmg: float = 0
        for enemy in enemies:
            enemy_mp = MapPoint.from_cell_id(enemy.disposition.cell_id)
            if enemy_mp not in impact_mps:
                continue
            if not is_included_by_mask(
                caster_id=self.game_state.player.character_id,
                caster_team=Team.TEAM_DEFENDER,
                masks=effect.targetMask.split(","),
                target_actor=enemy,
            ):
                continue
            decrease_by_dist_percent = (
                min(
                    effect.zoneDescr.damageDecreaseStepPercent
                    * target_mp.distance_to_map_point(enemy_mp),
                    effect.zoneDescr.maxDamageDecreaseApplyCount,
                )
                / 100
            )
            dmg: float = self.damage_calculator.get_damage_effect(effect) * (
                1 - decrease_by_dist_percent
            )
            enemy_total_dmg += dmg

        if "vol" in description_effect:
            thieft_life: float = enemy_total_dmg
        else:
            thieft_life = 0

        return enemy_total_dmg, thieft_life
