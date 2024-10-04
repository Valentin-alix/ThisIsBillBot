from dataclasses import dataclass, field

from src.core.logic.world.map import Map
from src.core.repositories.world_graph_reader import Vertex

HEURISTIC_SCALE: int = 1
INDOOR_WEIGHT: int = 0
MAX_ITERATION: int = 10000


@dataclass
class Node:
    vertex: Vertex
    target_vertexes: list[Vertex]
    parent: "Node | None" = field(default=None)
    closed: bool = field(init=False, default=False)

    def __post_init__(self):
        self.map = Map(self.vertex.m_mapId)
        if self.parent is not None:
            self.move_cost = self.parent.move_cost + 1

            manhattan_distance = min(
                abs(self.map.pos_x - Map(map_id=vertex.m_mapId).pos_x)
                + abs(self.map.pos_y - Map(map_id=vertex.m_mapId).pos_y)
                for vertex in self.target_vertexes
            )
            self.heuristic = HEURISTIC_SCALE * manhattan_distance
        else:
            self.move_cost = 0
            self.heuristic = 0

        self.total_cost = self.move_cost + self.heuristic
        self.map_id = self.vertex.m_mapId
