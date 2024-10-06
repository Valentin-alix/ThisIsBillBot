import os
from dataclasses import dataclass
from functools import cached_property
from typing import TypeAlias

import msgspec
from tqdm import tqdm

from db_dofus_unity.consts import DOFUS_PATH
from db_dofus_unity.gen.gen_standalone import WorldGraphRoot
from src.interfaces.metaclasses.singleton import Singleton

DataEdge: TypeAlias = WorldGraphRoot.ArrayItem2
Edge: TypeAlias = WorldGraphRoot.ArrayItem3 | WorldGraphRoot.ArrayItem6
OutGoingEdge: TypeAlias = WorldGraphRoot.ArrayItem6
Vertex: TypeAlias = WorldGraphRoot.ArrayItem1
Vertice: TypeAlias = WorldGraphRoot.ArrayItem


@dataclass(frozen=True)
class WorldGraphReader(metaclass=Singleton):
    def get_data_edge_by_src_vertex_uid(self) -> dict[int, DataEdge]:
        return dict(
            zip(self.datas.m_edges.m_keys.Array, self.datas.m_edges.m_values.Array)
        )

    def get_edge_by_src_and_dst_vertex(self, src: Vertex, dst: Vertex) -> Edge:
        data_edge = self.get_data_edge_by_src_vertex_uid()[src.m_uid]
        return dict(zip(data_edge.m_keys.Array, data_edge.m_values.Array))[dst.m_uid]

    def get_outgoing_edges_from_vertex(self, vertex: Vertex) -> list[Edge]:
        related_data: WorldGraphRoot.ArrayItem5 | None = dict(
            zip(
                self.datas.m_outgoingEdges.m_keys.Array,
                self.datas.m_outgoingEdges.m_values.Array,
            )
        ).get(vertex.m_uid)
        if related_data is None:
            return []
        return related_data.m_edgeList.Array

    def get_vertices_by_map_id(self) -> dict[int, Vertice]:
        return dict(
            zip(
                self.datas.m_vertices.m_keys.Array, self.datas.m_vertices.m_values.Array
            )
        )

    def get_vertex(self, map_id: int, map_rp_zone_id: int) -> Vertex | None:
        related_vertice = self.get_vertices_by_map_id().get(map_id)
        if related_vertice is None:
            return None

        return dict(zip(related_vertice.m_keys.Array, related_vertice.m_values.Array))[
            map_rp_zone_id
        ]

    @cached_property
    def datas(self) -> WorldGraphRoot.Model:
        with open(
            os.path.join(DOFUS_PATH, WorldGraphRoot.Model.FILE_PATH), "rb"
        ) as file:
            data = msgspec.json.decode(file.read(), type=WorldGraphRoot.Model)
        return data


if __name__ == "__main__":
    datas = WorldGraphReader().datas
    all_criteria: set[str] = set()
    for data_edge in tqdm(
        WorldGraphReader().get_data_edge_by_src_vertex_uid().values()
    ):
        for elem in data_edge.m_values.Array:
            for sub_elem in elem.m_transitions.Array:
                all_criteria.add(sub_elem.m_criterion)
