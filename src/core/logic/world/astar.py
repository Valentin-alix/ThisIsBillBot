from dataclasses import dataclass, field
from heapq import heappush, heappop

from db_dofus_unity.gen.gen_datas import MapPositionsRoot
from src.core.logic.criterions.group_item_criterion import GroupItemCriterion
from src.core.logic.grid.map_point import MapPoint
from src.core.logic.grid.path_finding.path_finding import Pathfinding
from src.core.logic.world.map import Map
from src.core.logic.world.node import Node
from src.core.repositories.world_graph_reader import Vertex, Edge, WorldGraphReader
from src.core.states.entity_state import EntityState
from src.core.states.inventory_state import InventoryState
from src.core.states.map_state import MapState
from src.core.states.objective_state import ObjectiveState
from src.core.states.player_state import PlayerState

HEURISTIC_SCALE: int = 1
INDOOR_WEIGHT: int = 0
MAX_ITERATION: int = 10000


@dataclass
class AStar:
    player_state: PlayerState
    map_state: MapState
    quest_state: ObjectiveState
    entity_state: EntityState
    inventory_state: InventoryState

    path_finding: Pathfinding
    src_vertex: Vertex
    dst_vertexes: list[Vertex]
    open_list: list[tuple[float, int, Node]] = field(
        init=False, default_factory=lambda: []
    )
    open_node_by_vertex_uid: dict[int, Node] = field(
        init=False, default_factory=lambda: {}
    )
    iterations: int = field(default=0, init=False)

    def __post_init__(self):
        self.dst_map_pos: list[MapPositionsRoot.Data] = [
            Map(vertex.m_mapId).position for vertex in self.dst_vertexes
        ]
        self.dst_map_id: list[int] = [vertex.m_mapId for vertex in self.dst_vertexes]

    def search(self) -> list[Edge] | None:
        if self.src_vertex in self.dst_vertexes:
            return []
        node = Node(Map(self.src_vertex.m_mapId).position, self.src_vertex, 0, 0)
        heappush(self.open_list, (0, id(node), node))
        return self.compute()

    def compute(self) -> list[Edge] | None:
        while self.open_list:
            if self.iterations > MAX_ITERATION:
                raise Exception("Too many iterations")
            self.iterations += 1
            _, _, current = heappop(self.open_list)
            if current.closed:
                continue
            current.closed = True
            if current.map_id in self.dst_map_id:
                result = self.build_path(current)
                return result

            edges = WorldGraphReader().get_outgoing_edges_from_vertex(current.vertex)
            for edge in edges:
                if not self.edge_has_valid_transitions(edge):
                    continue
                existing = self.open_node_by_vertex_uid.get(edge.m_to.m_uid)
                if existing is not None and current.cost + 1 < existing.cost:
                    continue

                edge_map = Map(edge.m_to.m_mapId)
                if edge_map is None:
                    continue
                cost_to_target = min(
                    abs(edge_map.position.posX - dst_map_pos.posX)
                    + abs(edge_map.position.posY - dst_map_pos.posY)
                    for dst_map_pos in self.dst_map_pos
                )
                node = Node(
                    edge_map.position,
                    edge.m_to,
                    current.cost + 1,
                    cost_to_target,
                    parent=current,
                )
                self.open_node_by_vertex_uid[edge.m_to.m_uid] = node
                heappush(self.open_list, (node.total_cost, id(node), node))

        return None

    def find_dst_cell(self, edge: Edge, mp: MapPoint) -> int | None:
        for reverse_edge in WorldGraphReader().get_outgoing_edges_from_vertex(
            edge.m_to
        ):
            if not reverse_edge.m_to == edge.m_from:
                continue
            for transition in reverse_edge.m_transitions.Array:
                if not transition.m_cellId:
                    continue
                mp_candidate = MapPoint.from_cell_id(transition.m_cellId)
                move_path = self.path_finding.find_path(mp, mp_candidate)
                if move_path.end.distance_to_cell_id(mp_candidate.cell_id) <= 2:
                    return mp_candidate.cell_id
        return None

    def edge_has_valid_transitions(self, edge: Edge) -> bool:
        criterion_white_list: list = [
            "Ad",
            "DM",
            "MI",
            "Mk",
            "Oc",
            "Pc",
            "QF",
            "Qo",
            "Qs",
            "Sv",
        ]
        for transition in edge.m_transitions.Array:
            if len(transition.m_criterion) == 0:
                continue
            if (
                "&" not in transition.m_criterion
                and "|" not in transition.m_criterion
                and transition.m_criterion[0:2] in criterion_white_list
            ):
                return False
            criterion = GroupItemCriterion(transition.m_criterion)
            if not criterion.is_respected(
                self.player_state,
                map_state=self.map_state,
                quest_state=self.quest_state,
                entity_state=self.entity_state,
                inventory_state=self.inventory_state,
            ):
                return False
        return True

    def build_path(self, node: Node) -> list[Edge]:
        result: list[Edge] = []
        while node.parent is not None:
            result.append(
                WorldGraphReader().get_edge_by_src_and_dst_vertex(
                    node.parent.vertex, node.vertex
                )
            )
            node = node.parent
        result.reverse()
        return result
