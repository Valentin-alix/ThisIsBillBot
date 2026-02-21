from dataclasses import dataclass
from functools import cached_property

import msgspec
from utils.cache import cache
from utils.singleton import Singleton

from DBDofusUnity.consts import STANDALONE_BUNDLES_ROOT
from DBDofusUnity.dofus_unity_reader.models.world_graph import Edge, Vertice, WorldGraphData


@dataclass(frozen=True)
class WorldGraphReader(metaclass=Singleton):
    def get_edge_by_src_and_dst_vertex(self, src: Vertice, dst: Vertice) -> Edge:
        return self.datas.m_edges[src.m_uid][dst.m_uid]

    def get_outgoing_edges_from_vertex(self, vertex: Vertice) -> list[Edge]:
        outgoing_edges = self.datas.m_outgoingEdges.get(vertex.m_uid)
        if outgoing_edges is None:
            return []
        return outgoing_edges.m_edgeList

    def get_vertex(self, map_id: int, linked_zone: int) -> Vertice | None:
        vertices_on_map = self.datas.m_vertices.get(map_id)
        if vertices_on_map is None:
            return None
        return vertices_on_map.get(linked_zone, None)

    def get_vertexes(self, map_id: int) -> set[Vertice]:
        return set(self.datas.m_vertices.get(map_id, {}).values())

    @cache
    def get_exit_cell_ids(self, map_id: int) -> frozenset[int]:
        """Cellules d'ou l'on quitte la map : portes, escaliers, zones de transition.

        Les elements interactifs poses dessus font changer de map ; tout comportement qui
        cherche un element "sur place" doit les ecarter.
        """
        return frozenset(
            transition.m_cellId
            for vertex in self.get_vertexes(map_id)
            for edge in self.get_outgoing_edges_from_vertex(vertex)
            for transition in edge.m_transitions
            if transition.m_cellId >= 0
        )

    @cached_property
    def get_all_transition_map_ids(self) -> set[int]:
        transition_map_ids: set[int] = set()
        for edge_by_id in self.datas.m_edges.values():
            for edge in edge_by_id.values():
                for transition in edge.m_transitions:
                    transition_map_ids.add(transition.m_transitionMapId)
        return transition_map_ids

    @cached_property
    def datas(self) -> WorldGraphData:
        with (STANDALONE_BUNDLES_ROOT / WorldGraphData.FILE_PATH).open("rb") as file:
            return msgspec.json.decode(file.read(), type=WorldGraphData)
