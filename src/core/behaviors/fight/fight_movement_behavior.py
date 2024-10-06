from collections import defaultdict
from dataclasses import dataclass

from db_dofus_unity.protos.game.common_pb2 import (
    ActorPositionInformation,
)
from src.core.behaviors.behavior import Behavior
from src.core.behaviors.movements.map_move_behavior import MapMoveBehavior
from src.core.logic.grid.map_point import MapPoint
from src.core.logic.grid.path_finding.movement_path import MovementPath
from src.core.logic.grid.path_finding.path_finding import Pathfinding
from src.core.states.entity_state import EntityState
from src.core.states.fight_state import FightState
from src.core.states.player_state import PlayerState
from src.interfaces.enums.stat_id import StatIds


@dataclass
class FightMovementBehavior(Behavior):
    map_move_behavior: MapMoveBehavior
    player_state: PlayerState
    path_finding: Pathfinding
    entity_state: EntityState
    fight_state: FightState

    def run(self) -> None:
        near_enemy_info = self.find_near_enemy_with_dist(self.player_state.map_point)
        if not near_enemy_info:
            return self.finish()

        enemy, move_path, _ = near_enemy_info
        pm: int = self.player_state.get_stat_usable_by_id(StatIds.MOVEMENT_POINTS)

        if len(move_path.path) > pm:
            move_path.end = move_path.path[pm].step
            move_path.path = move_path.path[:pm]

        self.map_move_behavior.start(
            parent=self, move_path=move_path, callback=self.finish
        )

    def find_near_enemy_with_dist(
        self, start: MapPoint
    ) -> tuple[ActorPositionInformation, MovementPath, float] | None:
        enemies = self.entity_state.get_enemies(self.fight_state.team)
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
