import sys
from dataclasses import dataclass

from PyQt5.QtWidgets import QApplication

from models.datas.spell_levels_root import SpellLevelsRoot, SpellLevelsRootItem, Effect
from protos.game.common_pb2 import (
    SpellModifierType,
    ActorPositionInformation,
    EntityDisposition,
)
from src.common.logger import Logger
from src.core.data_center.data_reader import DataReader
from src.core.data_center.i18n import I18N
from src.core.data_center.map_reader import MapReader
from src.core.logic.fight.damage_calculator import DamageCalculator
from src.core.logic.fight.los_detector import LosDetector
from src.core.logic.fight.reachable_cells.fight_reachable_cells import (
    FightReachableCells,
)
from src.core.logic.fight.spell import (
    get_primary_spells,
    get_possible_mp_spell,
    get_ap_cost_spell,
    get_spell_max_cast_per_turn,
    does_spell_need_taken_cell,
    get_spell_max_cast_per_target,
    does_spell_need_test_los,
)
from src.core.logic.fight.spell_zone import get_zone_mps
from src.core.logic.grid.data_map_provider import DataMapProvider
from src.core.logic.grid.map_point import MapPoint
from src.core.logic.grid.path_finding.path_finding import Pathfinding
from src.core.states.game_state import GameState
from src.core.states.state_factory import StateFactory
from src.gui.components.graphics.grid_widget import GridView
from src.interfaces.enums.characteristic_enum import CharacteristicEnum
from src.interfaces.enums.spell_shape_enum import SpellShapeEnum
from src.signals.grid_signals import GridSignals
from src.signals.log_signals import LogSignals
from src.signals.player_signals import GameInfoSignals
from src.signals.world_signals import MapSignals


@dataclass
class Attacker:
    game_state: GameState
    fight_reachable_cells: FightReachableCells
    damage_calculator: DamageCalculator
    path_finding: Pathfinding
    logger: Logger

    def get_valid_spells_for_turn(self) -> list[tuple[SpellLevelsRootItem, Effect]]:
        primary_spells = get_primary_spells(
            self.game_state.fight.spells, self.game_state.fight.primary_elem
        )
        valid_spell_levels: list[tuple[SpellLevelsRootItem, Effect]] = []
        for spell_lvl, effect in primary_spells:
            spell_ap_cost = get_ap_cost_spell(
                spell_lvl,
                self.game_state.fight.modifier_by_type_and_spell_id.get(
                    (spell_lvl.spellId, SpellModifierType.AP_COST)
                ),
            )
            if spell_ap_cost > self.game_state.player.get_stat_by_id(
                CharacteristicEnum.ACTION_POINTS
            ):
                continue
            if (
                spell_lvl.initialCooldown != 0
                and spell_lvl.initialCooldown > self.game_state.fight.fight_turn
            ):
                continue

            last_triggered_turn = (
                self.game_state.fight.last_triggered_turn_by_spell_id.get(
                    spell_lvl.spellId, None
                )
            )
            if (
                spell_lvl.globalCooldown != 0
                and last_triggered_turn is not None
                and self.game_state.fight.fight_turn - last_triggered_turn
                < spell_lvl.globalCooldown
            ):
                continue

            max_cast_per_turn = get_spell_max_cast_per_turn(
                spell_lvl,
                self.game_state.fight.modifier_by_type_and_spell_id.get(
                    (spell_lvl.spellId, SpellModifierType.MAX_CAST_PER_TURN)
                ),
            )
            count_casted_by_target_by_spell_id = (
                self.game_state.fight.count_casted_by_target_by_spell_id.get(
                    spell_lvl.spellId
                )
            )
            if (
                count_casted_by_target_by_spell_id is not None
                and max_cast_per_turn != 0
                and max_cast_per_turn
                <= sum(count_casted_by_target_by_spell_id.values())
            ):
                continue
            valid_spell_levels.append((spell_lvl, effect))
        return valid_spell_levels

    def find_best_attack_from_mp(
        self,
    ) -> tuple[MapPoint, SpellLevelsRootItem, MapPoint] | None:
        """get the attack that do the most damage with less ap"""
        best_attack: (
            tuple[float, int, MapPoint, SpellLevelsRoot.Data, MapPoint] | None
        ) = None

        entities_by_mp: dict[MapPoint, ActorPositionInformation] = {
            MapPoint.from_cell_id(actor.disposition.cell_id): actor
            for actor in self.game_state.entity.actor_by_id.values()
        }
        enemies_mp = {
            MapPoint.from_cell_id(enemy.disposition.cell_id)
            for enemy in self.game_state.entity.get_enemies(self.game_state.fight.team)
        }
        entities_mp: set[MapPoint] = set(entities_by_mp.keys())
        allies_mp: set[MapPoint] = {
            ally_mp for ally_mp in entities_mp if ally_mp not in enemies_mp
        }
        movable_mps = self.fight_reachable_cells.search(
            enemies_mp=enemies_mp, entities_mp=entities_mp
        )
        movable_mps[self.game_state.player.map_point] = (
            self.game_state.player.get_stat_by_id(CharacteristicEnum.MOVEMENT_POINTS)
        )
        health_percentage = self.game_state.player.life_percentage
        self.logger.info(
            f"find from mp {self.game_state.player.map_point} with entities {entities_by_mp} and enemies "
            f"mp : {enemies_mp}"
        )
        valid_spells_for_turn = self.get_valid_spells_for_turn()
        for spell_lvl, effect in valid_spells_for_turn:
            data_effect = DataReader().effect_by_id[effect.effectId]
            description_effect = I18N.name_by_id[data_effect.descriptionId]

            for movable_mp, remaining_pm in movable_mps.items():
                targetable_mps = get_possible_mp_spell(
                    movable_mp,
                    spell_lvl,
                    self.game_state.player.get_stat_by_id(CharacteristicEnum.RANGE),
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
                if does_spell_need_taken_cell(spell_lvl):
                    targetable_mps &= entities_mp

                for targetable_mp in targetable_mps:
                    targetable_mp_data = MapReader().get_cell_data_by_cell_id(
                        self.game_state.map.map_id, targetable_mp.cell_id
                    )
                    if not targetable_mp_data.mov or not targetable_mp_data.los:
                        continue

                    max_cast_per_target = get_spell_max_cast_per_target(
                        spell_lvl,
                        self.game_state.fight.modifier_by_type_and_spell_id.get(
                            (
                                spell_lvl.spellId,
                                SpellModifierType.MAX_CAST_PER_TARGET,
                            )
                        ),
                    )
                    count_casted_by_target_id = (
                        self.game_state.fight.count_casted_by_target_by_spell_id.get(
                            spell_lvl.spellId
                        )
                    )
                    entity_target = entities_by_mp.get(targetable_mp)
                    if (
                        count_casted_by_target_id is not None
                        and entity_target is not None
                        and max_cast_per_target != 0
                        and max_cast_per_target
                        <= count_casted_by_target_id.get(entity_target.actor_id, 0)
                    ):
                        continue

                    if does_spell_need_test_los(
                        spell_lvl
                    ) and not LosDetector.los_between(
                        map_id=self.game_state.map.map_id,
                        taken_mps=entities_mp,
                        start=movable_mp,
                        end=targetable_mp,
                    ):
                        continue

                    direction = movable_mp.orientation_to(targetable_mp)
                    impact_mps = zone_spell.get_mps(
                        mp=targetable_mp, direction=direction
                    )

                    spell_ap_cost = get_ap_cost_spell(
                        spell_lvl,
                        self.game_state.fight.modifier_by_type_and_spell_id.get(
                            (spell_lvl.spellId, SpellModifierType.AP_COST)
                        ),
                    )

                    enemy_dmg: int = 0
                    enemy_dmg_summoned: int = 0
                    for enemy_mp in enemies_mp:
                        if enemy_mp not in impact_mps:
                            continue
                        enemy_entity = entities_by_mp[enemy_mp]
                        if not (
                            enemy_entity.HasField("actor_information")
                            and enemy_entity.actor_information.HasField("fighter")
                            and enemy_entity.actor_information.fighter.HasField(
                                "ai_fighter"
                            )
                        ):
                            continue
                        monster_info = (
                            enemy_entity.actor_information.fighter.ai_fighter.monster_fighter_information
                        )
                        monster_id, monster_grade = (
                            monster_info.monster_gid,
                            monster_info.creature_grade,
                        )
                        monster = DataReader().monsters_by_id[monster_id]
                        monster_grade = monster.grades[monster_grade - 1]
                        dmg = self.damage_calculator.get_damage_effect(
                            effect, monster_grade
                        )
                        dmg -= targetable_mp.distance_to_map_point(enemy_mp) * 0.1
                        if enemy_mp in self.game_state.entity.summoned_mps:
                            enemy_dmg_summoned += dmg
                        else:
                            enemy_dmg += dmg

                    ally_count_hit: int = 0
                    ally_summoned_count_hit: int = 0
                    for ally_mp in allies_mp:
                        if ally_mp not in impact_mps:
                            continue
                        if ally_mp not in self.game_state.entity.summoned_mps:
                            ally_count_hit += 1
                        else:
                            ally_summoned_count_hit += 1

                    dmg_weight = (enemy_dmg + enemy_dmg_summoned / 4) / (
                        (1 + ally_count_hit / 2 + ally_summoned_count_hit / 8)
                    )
                    total_weight_spell = dmg_weight / spell_ap_cost
                    if "vol" in description_effect:
                        total_weight_spell /= health_percentage

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

        return (
            (best_attack[2], best_attack[3], best_attack[4])
            if best_attack is not None and best_attack[0] > 0
            else None
        )


if __name__ == "__main__":
    game_info_signals = GameInfoSignals()
    grid_signals = GridSignals()
    debug_signals = MapSignals()
    logger = Logger(LogSignals())
    game_state = StateFactory.create_game_state(
        game_info_signals, grid_signals, logger=logger
    )
    data_map_provider = DataMapProvider(game_state=game_state)
    path_finding = Pathfinding(
        data_map_provider=data_map_provider, game_state=game_state, logger=logger
    )
    application = QApplication(sys.argv)
    widget = GridView(grid_signals=grid_signals, debug_signals=debug_signals)

    game_state.map.map_id = 189533195
    game_state.entity.set_actors(
        [
            ActorPositionInformation(
                actor_id=0, disposition=EntityDisposition(cell_id=297)
            ),
            ActorPositionInformation(
                actor_id=1, disposition=EntityDisposition(cell_id=304)
            ),
            ActorPositionInformation(
                actor_id=2, disposition=EntityDisposition(cell_id=425)
            ),
        ]
    )
    enemies_mp = {
        MapPoint.from_cell_id(425),
    }
    fight_reachable_cells = FightReachableCells(game_state=game_state)

    widget.on_new_map_id(game_state.map.map_id)
    debug_signals.white_cell.emit(player_mp)
    debug_signals.red_cells.emit(enemies_mp)

    attacker = Attacker(
        game_state=game_state,
        fight_reachable_cells=fight_reachable_cells,
        path_finding=path_finding,
    )
    attack = attacker.find_best_attack_from_mp()
    game_state.player.characteristic_by_id[CharacteristicEnum.ACTION_POINTS] = 9
    game_state.player.characteristic_by_id[CharacteristicEnum.MOVEMENT_POINTS] = 6

    if attack:
        spell = DataReader().spell_by_id[attack[2].spellId]
        print(
            attack[1],
            attack[-1],
            I18N.name_by_id[spell.nameId],
            attack[2].spellId,
        )
        debug_signals.white_cell.emit(attack[1].end)
        debug_signals.white_cell.emit(attack[-1])

    widget.show()

    application.exec()
