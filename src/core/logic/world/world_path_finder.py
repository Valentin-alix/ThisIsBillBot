from dataclasses import dataclass


from models.world_graph import Vertice, Edge
from data_center.world_graph_reader import WorldGraphReader
from src.core.logic.grid.path_finding.path_finding import Pathfinding
from src.core.logic.world.astar_vertice import AstarWorld
from src.core.states.game_state import GameState


@dataclass
class WorldPathFinder:
    path_finding: Pathfinding
    game_state: GameState

    astar_world: AstarWorld

    def find_path(
        self, src_vertex: Vertice, dst_map_ids: set[int], linked_zone: int | None = None
    ) -> list[Edge] | None:
        dst_vertexes: set[Vertice]
        if linked_zone is not None:
            dst_vertexes = {
                vertex
                for dst_map_id in dst_map_ids
                if (vertex := WorldGraphReader().get_vertex(dst_map_id, linked_zone))
                is not None
            }
        else:
            dst_vertexes = {
                vertex
                for dst_map_id in dst_map_ids
                for vertex in WorldGraphReader().get_vertexes(dst_map_id)
            }

        if src_vertex in dst_vertexes:
            return []

        if len(dst_vertexes) == 0:
            return None
        path = self.astar_world.find_path(start=src_vertex, ends=dst_vertexes)
        return path
