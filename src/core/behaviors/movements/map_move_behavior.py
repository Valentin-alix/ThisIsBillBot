from dataclasses import dataclass

from db_dofus_unity.protos.game.gamemap_pb2 import (
    MapMovementRequest,
    MapMovementConfirmRequest,
)
from src.common.logger import Logger
from src.core.behaviors.behavior import Behavior
from src.core.logic.grid.map_point import MapPoint
from src.core.logic.grid.path_finding.movement_path import MovementPath
from src.core.logic.grid.path_finding.path_finding import Pathfinding
from src.core.states.fight_state import FightState
from src.core.states.map_state import MapState
from src.core.states.player_state import PlayerState


@dataclass
class MapMoveBehavior(Behavior):
    fight_state: FightState
    player_state: PlayerState
    map_state: MapState
    path_finding: Pathfinding

    def run(self, move_path: MovementPath):
        Logger().info(f"Going to : {move_path.end}")
        if self.player_state.map_point.cell_id == move_path.end.cell_id:
            return self.finish()
        key_cells = move_path.get_key_cells()
        self.event_manager.on(
            MapMovementConfirmRequest,
            callback=lambda _: self.finish(),
            originator=self,
            once=True,
        )
        map_movement_request = MapMovementRequest(
            key_cells=key_cells, map_id=self.map_state.map_id
        )
        self.event_manager.send(map_movement_request)

    def get_move_path_to_cell_id(self, cell_id: int):
        if self.player_state.map_point.cell_id == cell_id:
            return
        end_map_point = MapPoint.from_cell_id(cell_id)

        movement_path = self.path_finding.find_path(
            self.player_state.map_point,
            end_map_point,
            allow_diag=not self.fight_state.in_fight,
            allow_trough_entity=not self.fight_state.in_fight,
        )
        return movement_path
