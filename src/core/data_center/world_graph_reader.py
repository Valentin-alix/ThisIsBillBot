import os
import zlib
from dataclasses import dataclass
from functools import cached_property

import msgspec

from D3Database.consts import D3_DATABASE
from models.world_graph import WorldGraphData, Edge, Vertice
from src.interfaces.metaclasses.singleton import Singleton


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

    @cached_property
    def datas(self) -> WorldGraphData:
        with open(os.path.join(D3_DATABASE, WorldGraphData.FILE_PATH), "rb") as file:
            data = msgspec.json.decode(
                zlib.decompress(file.read()), type=WorldGraphData
            )
        return data


if __name__ == "__main__":
    v1 = WorldGraphReader().get_vertex(193331715, 1)
    v2 = WorldGraphReader().get_vertex(193331716, 2)
    e3 = WorldGraphReader().get_outgoing_edges_from_vertex(v1)
    edge = WorldGraphReader().get_edge_by_src_and_dst_vertex(v1, v2)
    print(e3)
