from dataclasses import dataclass

from com.ankama.dofus.server.game.protocol.gamemap_pb2 import (
    MapMovementRequest,
)
from src.core.logic.grid.map_point import MapPoint
from src.core.logic.grid.path_finding.movement_path import MovementPath
from src.core.logic.grid.path_finding.path_finding import Pathfinding
from src.core.states.map_state import MapState
from src.core.states.player_state import PlayerState
from src.signals.message_events import MessageEvents


@dataclass
class MapBehavior:
    msg_event: MessageEvents
    player_state: PlayerState
    map_state: MapState
    path_finding: Pathfinding

    def send_move_path(self, move_path: MovementPath):
        key_cells = move_path.get_key_cells()
        map_movement_request = MapMovementRequest(
            key_cells=key_cells, map_id=self.map_state.map.map_id
        )
        self.msg_event.send_game_msg.send(map_movement_request)

    def go_to_cell_id(self, cell_id: int):
        if self.player_state.map_point.map_point == cell_id:
            return
        end_map_point = MapPoint.from_cell_id(cell_id)

        movement_path = self.path_finding.find_path(
            self.player_state.map_point,
            end_map_point,
            allow_diag=not self.player_state.is_in_fight,
            allow_trough_entity=not self.player_state.is_in_fight,
            avoid_obstacles=True,
        )
        self.send_move_path(movement_path)
