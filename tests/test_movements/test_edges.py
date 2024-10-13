import unittest
from data_center.data_reader import DataReader
from data_center.world_graph_reader import WorldGraphReader
from src.core.logic.world.edge import FORBIDDEN_MAP_IDS


class TestEdges(unittest.TestCase):
    def test_forbidden_map_ids(self):
        for map_id in FORBIDDEN_MAP_IDS:
            map_data = DataReader().map_pos_by_map_id[map_id]
            print(map_id, map_data.posX, map_data.posY)

    def test_valid_edge_transition(self):
        map_id = 168034308
        map_data = DataReader().map_pos_by_map_id[map_id]
        print(map_data.posX, map_data.posY)
        vertices = WorldGraphReader().datas.m_vertices.get(map_id)
        assert vertices is not None
        print(len(vertices))
        edges = WorldGraphReader().get_outgoing_edges_from_vertex(
            next(iter(vertices.values()))
        )
        print(edges)
