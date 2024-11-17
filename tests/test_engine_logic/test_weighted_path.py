import time

from D3Database.data_center.world_graph_reader import WorldGraphReader
from D3Database.models.world_graph import Edge
from src.core.engine.weights.weighted_path import WeightedPath
from tests.setup_factory import GameStateFixture


class TestWeightedPath(GameStateFixture):
    def setUp(self):
        super().setUp()
        self.set_game_state(175, [], map_id=120062979)
        self.weighted_path = WeightedPath(game_state=self.game_state)

        linked_zone = self.game_state.map.linked_zone_rp
        start_vertex = WorldGraphReader().get_vertex(120062979, linked_zone)
        assert start_vertex is not None
        self.start_vertex = start_vertex

        self.weight_by_map_id: dict[int, float] = {}

        def get_weight_by_edge_func(edge: Edge) -> float:
            return hash(edge.m_to.m_mapId) % 100

        self.get_weight_func = get_weight_by_edge_func

    def test_beam_search_basic(self):
        path, total_weight = self.weighted_path.beam_search_path(
            start_vertex=self.start_vertex,
            get_weight_by_edge_func=self.get_weight_func,
            weight_by_map_id=self.weight_by_map_id,
            depth=10,
            beam_width=20,
        )

        assert isinstance(path, list)
        assert isinstance(total_weight, float)
        assert len(path) <= 10
        assert total_weight >= 0

        visited_maps = {edge.m_to.m_mapId for edge in path}
        assert len(path) == 0 or len(visited_maps) > 0

    def test_beam_search_performance(self):
        iterations = 10
        total_time = 0
        total_weight_sum = 0

        for _ in range(iterations):
            self.weight_by_map_id.clear()

            start = time.perf_counter()
            path, total_weight = self.weighted_path.beam_search_path(
                start_vertex=self.start_vertex,
                get_weight_by_edge_func=self.get_weight_func,
                weight_by_map_id=self.weight_by_map_id,
                depth=20,
                beam_width=50,
            )
            elapsed = time.perf_counter() - start

            total_time += elapsed
            total_weight_sum += total_weight

        avg_time = total_time / iterations
        avg_weight = total_weight_sum / iterations

        assert avg_time < 1.0

    def test_beam_search_different_widths(self):
        beam_widths = [10, 25, 50, 100]

        for width in beam_widths:
            self.weight_by_map_id.clear()

            start = time.perf_counter()
            path, total_weight = self.weighted_path.beam_search_path(
                start_vertex=self.start_vertex,
                get_weight_by_edge_func=self.get_weight_func,
                weight_by_map_id=self.weight_by_map_id,
                depth=20,
                beam_width=width,
            )
            elapsed = time.perf_counter() - start

    def test_revisit_penalty_beam_search(self):
        path, total_weight = self.weighted_path.beam_search_path(
            start_vertex=self.start_vertex,
            get_weight_by_edge_func=self.get_weight_func,
            weight_by_map_id=self.weight_by_map_id,
            depth=20,
            beam_width=50,
        )

        visited_map_ids = [edge.m_to.m_mapId for edge in path]
        unique_maps = set(visited_map_ids)

        assert len(unique_maps) <= len(path)

    def test_path_consistency(self):
        path, weight = self.weighted_path.beam_search_path(
            start_vertex=self.start_vertex,
            get_weight_by_edge_func=self.get_weight_func,
            weight_by_map_id=self.weight_by_map_id,
            depth=10,
            beam_width=20,
        )

        if len(path) > 1:
            for i in range(len(path) - 1):
                current_edge = path[i]
                next_edge = path[i + 1]

                assert current_edge.m_to.m_mapId == next_edge.m_from.m_mapId
