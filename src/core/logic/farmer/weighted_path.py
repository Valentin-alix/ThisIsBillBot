import random
import sys
from dataclasses import dataclass
from time import perf_counter
from typing import Callable

from PyQt5.QtWidgets import QApplication

from models.world_graph import Vertice, Edge
from src.common.logger import Logger
from src.core.data_center.data_reader import DataReader
from src.core.data_center.i18n import I18N
from src.core.data_center.world_graph_reader import WorldGraphReader
from src.core.logic.farmer.collectables import get_gfx_to_item_and_job
from src.core.logic.farmer.weight_collectables import (
    get_map_id_collectable_weight,
)
from src.core.logic.grid.map_point import MapPoint
from src.core.logic.world.edge import (
    iter_valid_outgoing_edges,
    draw_edge_path,
)
from src.core.logic.world.linked_zone import get_linked_zone_rp
from src.core.states.game_state import GameState
from src.core.states.state_factory import StateFactory
from src.gui.components.graphics.map_world_widget import MapWorldView
from src.signals.grid_signals import GridSignals
from src.signals.log_signals import LogSignals
from src.signals.player_signals import GameInfoSignals
from src.signals.world_signals import WorldSignals


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


if __name__ == "__main__":
    grid_signals = GridSignals()
    game_info_signals = GameInfoSignals()
    game_state = StateFactory.create_game_state(
        game_info_signals, grid_signals, logger=Logger(LogSignals())
    )
    world_signals = WorldSignals()

    start_map_id = 142089739
    start_mp = MapPoint.from_cell_id(340)
    start_data_map = DataReader().map_pos_by_map_id[start_map_id]
    linked_zone = get_linked_zone_rp(map_id=start_map_id, cell_id=start_mp.cell_id)
    vertex = WorldGraphReader().get_vertex(start_map_id, linked_zone)

    application = QApplication(sys.argv)

    widget = MapWorldView(world_signals)

    widget.show()

    map_ids: set[int] = set()
    area = DataReader().area_by_id[
        DataReader().sub_area_by_id[start_data_map.subAreaId].areaId
    ]
    print(I18N.name_by_id[area.nameId])
    for sub_area_id in DataReader().sub_areas_by_area_id[area.id]:
        map_ids |= set(DataReader().sub_area_by_id[sub_area_id].mapIds)

    add_weight = {}
    for map_id in map_ids:
        add_weight[map_id] = get_map_id_collectable_weight(
            map_id, get_gfx_to_item_and_job(), {}, {}
        )

    weighted_path = WeightedPath(game_state=game_state)

    max_weight = max(add_weight.values())

    def get_weight(map_id: int) -> float:
        weight = add_weight.get(map_id, -1)
        map_data = DataReader().map_pos_by_map_id[map_id]
        weight_color = int(255 * (weight / max_weight))
        world_signals.color_pos.emit(map_data, (255, 255 - weight_color, 0))
        return weight

    print(len(map_ids))

    before = perf_counter()
    # path, weight = weighted_path.get_best_path(
    #     vertex, frozenset(), get_weight, {}, [], {}, depth_remaining=11
    # )
    path, weight = weighted_path.monte_carlo_path(vertex, get_weight, {})
    print(weight, len(path))
    print(perf_counter() - before)
    path_map_ids = [edge.m_to.m_mapId for edge in path]
    # print(TEMP)
    draw_edge_path(world_signals, path)
    # path = weighted_path.dfs_dynamic_max_weight(vertex, 100, {}, add_weight)

    application.exec()
