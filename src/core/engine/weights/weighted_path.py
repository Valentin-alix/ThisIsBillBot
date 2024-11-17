from dataclasses import dataclass
from heapq import nlargest
from typing import Callable

from D3Database.models.world_graph import Edge, Vertice
from src.core.engine.movements.world.edge import iter_valid_outgoing_edges
from src.core.states.game_state import GameState


@dataclass
class WeightedPath:
    game_state: GameState

    def get_weight_edge(
        self,
        edge: Edge,
        get_weight_by_edge_func: Callable[[Edge], float],
        weight_by_map_id: dict[int, float],
    ):
        if weight_by_map_id.get(edge.m_to.m_mapId) is None:
            weight_by_map_id[edge.m_to.m_mapId] = get_weight_by_edge_func(edge)
        return weight_by_map_id[edge.m_to.m_mapId]

    def beam_search_path(
        self,
        start_vertex: Vertice,
        get_weight_by_edge_func: Callable[[Edge], float],
        weight_by_map_id: dict[int, float],
        depth: int = 25,
        beam_width: int = 50,
    ) -> tuple[list[Edge], float]:
        """
        Deterministic weighted path search using Beam Search.
        """

        # (current_vertex, path, score, visited_map_ids)
        beam: list[tuple[Vertice, list[Edge], float, tuple[int, ...]]] = [
            (start_vertex, [], 0.0, (start_vertex.m_mapId,))
        ]

        for _ in range(depth):
            candidates = []

            for vertice, path, score, visited in beam:
                for edge in iter_valid_outgoing_edges(vertice, self.game_state):
                    base_weight = self.get_weight_edge(
                        edge,
                        get_weight_by_edge_func,
                        weight_by_map_id,
                    )

                    if edge.m_to.m_mapId in visited:
                        idx = visited.index(edge.m_to.m_mapId)
                        steps_since_visit = idx
                        penalty = 0.1 ** max(1, 5 - steps_since_visit)
                        weight = base_weight * penalty
                    else:
                        weight = base_weight

                    candidates.append(
                        (
                            edge.m_to,
                            path + [edge],
                            score + weight,
                            (edge.m_to.m_mapId,) + visited,
                        )
                    )

            if not candidates:
                break

            beam = nlargest(beam_width, candidates, key=lambda x: x[2])

        best = max(beam, key=lambda x: x[2])
        return best[1], best[2]
