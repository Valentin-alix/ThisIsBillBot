from dataclasses import dataclass, field
from heapq import heappush, heappop

from src.core.logic.grid.map_point import MapPoint
from src.core.logic.grid.path_finding.path_finding import Pathfinding
from src.core.logic.world.node import Node
from src.core.repositories.world_graph_reader import Vertex, Edge, WorldGraphReader

HEURISTIC_SCALE: int = 1
INDOOR_WEIGHT: int = 0
MAX_ITERATION: int = 10000


@dataclass
class AStar:
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

    def search(self) -> list[Edge] | None:
        if self.src_vertex in self.dst_vertexes:
            return []

        node = Node(self.src_vertex, self.dst_vertexes)
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
            if current.vertex in self.dst_vertexes:
                result = AStar.build_path(current)
                return result

            edges = WorldGraphReader().get_outgoing_edges_by_src_uid(
                current.vertex.m_uid
            )
            for edge in edges:
                if not AStar.edge_has_valid_transition(edge):
                    continue
                existing = self.open_node_by_vertex_uid.get(edge.m_to.m_uid)
                if existing is None or current.move_cost + 1 < existing.move_cost:
                    node = Node(edge.m_to, self.dst_vertexes, current)
                    self.open_node_by_vertex_uid[edge.m_to.m_uid] = node
                    heappush(self.open_list, (node.total_cost, id(node), node))

        return None

    def find_dst_cell(self, edge: Edge, mp: MapPoint) -> int | None:
        for reverse_edge in WorldGraphReader().get_outgoing_edges_by_src_uid(
            edge.m_to.m_uid
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

    @staticmethod
    def edge_has_valid_transition(edge: Edge) -> bool:
        valid: bool = False
        for transition in edge.m_transitions.Array:
            if not transition.m_criterion:
                valid = True
                continue
            return False
        return valid

    @staticmethod
    def build_path(node: Node) -> list[Edge]:
        result = list[Edge]()
        while node.parent is not None:
            result.append(
                WorldGraphReader().get_edge_by_src_dst_vertex_uid(
                    node.parent.vertex.m_uid, node.vertex.m_uid
                )
            )
            node = node.parent
        result.reverse()
        return result
