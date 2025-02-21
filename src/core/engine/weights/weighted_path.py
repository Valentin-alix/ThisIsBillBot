from dataclasses import dataclass
from heapq import nlargest
from typing import Callable

from dofus_unity_reader.models.world_graph import Edge, Vertice

from src.core.engine.contexts import WorldTransitionContext
from src.core.engine.movements.world.edge import iter_valid_outgoing_edges


@dataclass
class WeightedPath:
    def get_weight_edge(
        self,
        edge: Edge,
        get_weight_by_edge_func: Callable[[Edge], float],
        weight_by_map_id: dict[int, float],
    ) -> float:
        if weight_by_map_id.get(edge.m_to.m_mapId) is None:
            weight_by_map_id[edge.m_to.m_mapId] = get_weight_by_edge_func(edge)
        return weight_by_map_id[edge.m_to.m_mapId]

    def beam_search_path(
        self,
        start_vertex: Vertice,
        context: WorldTransitionContext,
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
            candidates: list[tuple[Vertice, list[Edge], float, tuple[int, ...]]] = []

            for vertice, path, score, visited in beam:
                for edge in iter_valid_outgoing_edges(vertice, context):
                    base_weight = self.get_weight_edge(
                        edge,
                        get_weight_by_edge_func,
                        weight_by_map_id,
                    )

                    if base_weight <= 0:
                        continue

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
