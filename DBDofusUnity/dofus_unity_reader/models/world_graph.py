from msgspec import Struct


class Transition(Struct, frozen=True):
    m_type: int
    m_direction: int
    m_skillId: int
    m_criterion: str
    m_transitionMapId: int
    m_cellId: int
    m_id: int


class Vertice(Struct, frozen=True):
    m_mapId: int
    m_zoneId: int
    m_uid: int

    def __hash__(self) -> int:
        return (self.m_mapId, self.m_zoneId).__hash__()

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, Vertice) and self.m_mapId == other.m_mapId and self.m_zoneId == other.m_zoneId
        )


class Edge(Struct, frozen=True):
    m_from: Vertice
    m_to: Vertice
    m_transitions: list[Transition]

    def __hash__(self) -> int:
        return (self.m_from, self.m_to).__hash__()

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Edge) and other.m_from == self.m_from and other.m_to == self.m_to


class OutgoingEdge(Struct, frozen=True):
    m_edgeList: list[Edge]


class WorldGraphData(Struct, frozen=True):
    FILE_PATH = "world-graph.json"

    m_vertices: dict[int, dict[int, Vertice]]  # Vertice by zone ID by map ID.
    m_edges: dict[int, dict[int, Edge]]  # Edge by destination UID by source UID.
    m_outgoingEdges: dict[int, OutgoingEdge]  # Outgoing edges by source UID.
