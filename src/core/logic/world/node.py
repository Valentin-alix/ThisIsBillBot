from dataclasses import dataclass, field

from db_dofus_unity.gen.gen_datas import MapPositionsRoot
from src.core.repositories.world_graph_reader import Vertex

HEURISTIC_SCALE: int = 1
INDOOR_WEIGHT: int = 0
MAX_ITERATION: int = 10000


@dataclass
class Node:
    map_pos: MapPositionsRoot.Data
    vertex: Vertex
    cost: int
    cost_to_target: int
    parent: "Node | None" = field(default=None)
    closed: bool = field(init=False, default=False)

    def __post_init__(self):
        self.total_cost = self.cost + self.cost_to_target
        self.map_id = self.vertex.m_mapId
