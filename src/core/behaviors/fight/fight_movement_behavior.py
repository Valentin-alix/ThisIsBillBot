from collections import defaultdict
from dataclasses import dataclass

from d3_mapping.resources.protos.game.common_pb2 import (
    ActorPositionInformation,
)
from enums.characteristic_enum import CharacteristicEnum
from grid.map_point import MapPoint

from src.core.behaviors.behavior import Behavior
from src.core.behaviors.movements.map_move_behavior import MapMoveBehavior
from src.core.logic.fight.reachable_cells.fight_reachable_cells import (
    FightReachableCells,
)
from src.core.logic.map.path_finding.movement_path import MovementPath
from src.core.logic.map.path_finding.path_finding import Pathfinding


@dataclass
class FightMovementBehavior(Behavior):
    map_move_behavior: MapMoveBehavior
    path_finding: Pathfinding
    fight_reachable_cells: FightReachableCells

    def run(
        self, move_path: MovementPath | None = None, run_away: bool = False
    ) -> None:
        if move_path is None:
            if run_away:
                move_path = self.find_safest_path()
                if move_path is None:
                    return self.finish()
            else:
                near_enemy_info = self.find_near_enemy_with_dist(
                    self.game_state.player.map_point
                )
                if not near_enemy_info:
                    return self.finish()

                move_path = near_enemy_info[1]

        pm: int = self.game_state.player.get_player_stat_by_id(
            CharacteristicEnum.MOVEMENT_POINTS
        )

        self.logger.info(f"PM : {pm}")

        if pm < 0:
            return self.finish()

        if len(move_path.path) > pm:
            move_path.end = move_path.path[pm].step
            move_path.path = move_path.path[:pm]

        self.map_move_behavior.start(
            parent=self, move_path=move_path, callback=self.finish
        )

    def find_near_enemy_with_dist(
        self, start: MapPoint
    ) -> tuple[ActorPositionInformation, MovementPath, float] | None:
        enemies = self.game_state.entity.get_enemies(
            self.game_state.player.character_id
        )
        if len(enemies) == 0:
            return None

        enemies_by_mp: dict[MapPoint, list[ActorPositionInformation]] = defaultdict(
            list
        )
        for enemy in enemies:
            mp_enemy = MapPoint.from_cell_id(enemy.disposition.cell_id)
            for side_mp_enemy in mp_enemy.side_map_points:
                enemies_by_mp[side_mp_enemy].append(enemy)

        move_path = self.path_finding.find_path(
            start,
            set(enemies_by_mp.keys()),
            allow_trough_entity=False,
            allow_diag=False,
        )

        related_enemies = enemies_by_mp.get(move_path.end)
        if related_enemies is None:
            near_mp, related_enemies = min(
                enemies_by_mp.items(),
                key=lambda mp_with_enemies: mp_with_enemies[0].distance_to_map_point(
                    move_path.end
                ),
            )
            cost_path = (
                len(move_path.path)
                + near_mp.distance_to_map_point(
                    MapPoint.from_cell_id(related_enemies[0].disposition.cell_id)
                )
                + 1
            )
        else:
            cost_path = len(move_path.path)

        return related_enemies[0], move_path, cost_path

    def find_safest_path(self) -> MovementPath | None:
        self.logger.info("Finding safest path")

        entities_mp: set[MapPoint] = {
            mp
            for mp, actors in self.game_state.entity.actors_on_mp.items()
            if len(actors) > 0
        }
        enemies_mp = {
            MapPoint.from_cell_id(enemy.disposition.cell_id)
            for enemy in self.game_state.entity.get_enemies(
                self.game_state.player.character_id
            )
        }

        self.logger.info(f"enemies mp : {enemies_mp}")

        reachable_mps = self.fight_reachable_cells.search(enemies_mp, entities_mp)
        if len(reachable_mps) == 0:
            return None

        mp_with_safest_coeff = max(
            (
                (
                    reachable_mp,
                    sum(
                        [
                            reachable_mp.distance_to_map_point(enemy_mp)
                            for enemy_mp in enemies_mp
                        ]
                    ),
                )
                for reachable_mp in reachable_mps
            ),
            key=lambda elem: elem[1],
        )

        self.logger.info(f"Found safest cell : {mp_with_safest_coeff}")

        move_path = self.path_finding.find_path(
            self.game_state.player.map_point,
            {mp_with_safest_coeff[0]},
            allow_trough_entity=False,
            allow_diag=False,
        )

        return move_path
