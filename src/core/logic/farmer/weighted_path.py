import random
from dataclasses import dataclass
from typing import Callable


from models.world_graph import Vertice, Edge
from src.core.logic.world.edge import (
    iter_valid_outgoing_edges,
)
from src.core.states.game_state import GameState


@dataclass
class WeightedPath:
    game_state: GameState

    def get_weight_edge(
        self,
        edge: Edge,
        get_weight_by_map_id_func: Callable[[int], float],
        weight_by_map_id: dict[int, float],
    ):
        if weight_by_map_id.get(edge.m_to.m_mapId) is None:
            weight_by_map_id[edge.m_to.m_mapId] = get_weight_by_map_id_func(
                edge.m_to.m_mapId
            )
        return weight_by_map_id[edge.m_to.m_mapId]

    def monte_carlo_path(
        self,
        start_vertex: Vertice,
        get_weight_by_map_id_func: Callable[[int], float],
        weight_by_map_id: dict[int, float],
        depth: int = 50,
        iterations: int = 1000,
    ):
        # heuristic, randomized weighted path
        best_weight: float = 0
        best_path: list[Edge] = []

        for _ in range(iterations):
            current_vertex = start_vertex
            visited_map_ids: list[int] = [current_vertex.m_mapId]
            total_weight: float = 0
            path: list[Edge] = []

            for _ in range(depth):
                edge_neighbors = [
                    neighbor
                    for neighbor in iter_valid_outgoing_edges(
                        current_vertex, self.game_state
                    )
                ]
                if not edge_neighbors:
                    break
                next_edge: Edge = random.choice(edge_neighbors)

                if next_edge.m_to.m_mapId in visited_map_ids:
                    continue

                weight = self.get_weight_edge(
                    next_edge,
                    weight_by_map_id=weight_by_map_id,
                    get_weight_by_map_id_func=get_weight_by_map_id_func,
                )

                path.append(next_edge)
                visited_map_ids.insert(0, next_edge.m_to.m_mapId)
                total_weight += weight
                current_vertex = next_edge.m_to

            if total_weight > best_weight:
                best_weight = total_weight
                best_path = path

        return best_path, best_weight

    def get_best_path(
        self,
        vertice: Vertice,
        visited_map_ids: frozenset[int],
        get_weight_by_map_id_func: Callable[[int], float],
        weight_by_map_id: dict[int, float],
        current_path: list[Edge],
        memo: dict[tuple[Vertice, int, frozenset[int]], float],
        curr_weight: float = 0,
        depth_remaining: int = 10,
    ) -> tuple[list[Edge], float]:
        if depth_remaining == 0:
            return current_path, curr_weight

        state = (vertice, depth_remaining, visited_map_ids)
        if state in memo:
            memo_weight = memo[state]
            return current_path, memo_weight

        max_weight = curr_weight
        best_path = current_path

        for edge in iter_valid_outgoing_edges(vertice, game_state=self.game_state):
            if edge.m_to.m_mapId in visited_map_ids:
                continue
            weight = self.get_weight_edge(
                edge, get_weight_by_map_id_func, weight_by_map_id
            )
            if weight is None:
                continue

            child_curr_path = current_path[::]
            child_curr_path.append(edge)
            child_path, child_weight = self.get_best_path(
                edge.m_to,
                visited_map_ids | {edge.m_to.m_mapId},
                get_weight_by_map_id_func,
                weight_by_map_id,
                current_path=child_curr_path,
                memo=memo,
                curr_weight=curr_weight + weight,
                depth_remaining=depth_remaining - 1,
            )
            if child_weight > max_weight:
                max_weight = child_weight
                best_path = child_path

        memo[state] = max_weight

        return best_path, max_weight
