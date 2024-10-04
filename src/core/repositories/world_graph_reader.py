import os
from dataclasses import dataclass
from functools import cached_property

import icecream
import msgspec
from tqdm import tqdm

from resources.gen.gen_standalone import WorldGraphRoot
from src.consts import DOFUS_FOLDER
from src.utils import Singleton

DataEdge = WorldGraphRoot.ArrayItem2
Edge = WorldGraphRoot.ArrayItem3 | WorldGraphRoot.ArrayItem6
OutGoingEdge = WorldGraphRoot.ArrayItem6
Vertex = WorldGraphRoot.ArrayItem1
Vertice = WorldGraphRoot.ArrayItem


@dataclass(frozen=True)
class WorldGraphReader(metaclass=Singleton):
    def get_data_edge_by_src_vertex_uid(self) -> dict[int, DataEdge]:
        return dict(
            zip(self.datas.m_edges.m_keys.Array, self.datas.m_edges.m_values.Array)
        )

    def get_edge_by_src_dst_vertex_uid(self, src_uid: int, dst_uid: int) -> Edge:
        data_edge = self.get_data_edge_by_src_vertex_uid()[src_uid]
        return dict(zip(data_edge.m_keys.Array, data_edge.m_values.Array))[dst_uid]

    def get_outgoing_edges_by_src_uid(self, src_uid: int) -> list[Edge]:
        related_data: WorldGraphRoot.ArrayItem5 = dict(
            zip(
                self.datas.m_outgoingEdges.m_keys.Array,
                self.datas.m_outgoingEdges.m_values.Array,
            )
        )[src_uid]
        return related_data.m_edgeList.Array

    def get_vertices_by_map_id(self) -> dict[int, Vertice]:
        return dict(
            zip(
                self.datas.m_vertices.m_keys.Array, self.datas.m_vertices.m_values.Array
            )
        )

    def get_vertex(self, map_id: int, map_rp_zone_id: int) -> Vertex:
        related_vertice = self.get_vertices_by_map_id()[map_id]

        related_vertex_key = related_vertice.m_keys.Array.index(map_rp_zone_id)
        related_vertex = related_vertice.m_values.Array[related_vertex_key]
        return related_vertex

    @cached_property
    def datas(self) -> WorldGraphRoot.WorldGraphModel:
        with open(
            os.path.join(DOFUS_FOLDER, WorldGraphRoot.WorldGraphModel.FILE_PATH), "rb"
        ) as file:
            data = msgspec.json.decode(file.read(), type=WorldGraphRoot.WorldGraphModel)
        return data


if __name__ == "__main__":
    datas = WorldGraphReader().datas
    all_criterions: set[str] = set()
    for data_edge in tqdm(
        WorldGraphReader().get_data_edge_by_src_vertex_uid().values()
    ):
        for elem in data_edge.m_values.Array:
            for sub_elem in elem.m_transitions.Array:
                all_criterions.add(sub_elem.m_criterion)

    icecream.ic(all_criterions)
