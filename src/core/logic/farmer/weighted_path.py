import sys
from dataclasses import dataclass
from time import perf_counter
from typing import Callable

from PyQt5.QtWidgets import QApplication

from models.world_graph import Vertice, Edge
from src.common.logger import Logger
from src.core.data_center.data_reader import DataReader
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

DEPTH = 30


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

    def get_best_path(
        self,
        vertice: Vertice,
        visited_map_ids: set[int],
        get_weight_by_map_id_func: Callable[[int], float],
        weight_by_map_id: dict[int, float],
        current_path: list[Edge],
        memo: dict[tuple[Vertice, int], float],
        curr_weight: float = 0,
        depth_remaining: int = DEPTH,
    ) -> tuple[list[Edge], float]:
        if depth_remaining == 0:
            return current_path, curr_weight

        if (vertice, depth_remaining) in memo:
            memo_weight = memo[(vertice, depth_remaining)]
            return current_path, memo_weight

        visited_map_ids.add(vertice.m_mapId)
        max_weight = curr_weight
        best_path = current_path

        for edge in iter_valid_outgoing_edges(vertice, game_state=self.game_state):
            if edge.m_to.m_mapId in visited_map_ids:
                continue

            child_curr_path = current_path[::]
            child_curr_path.append(edge)
            weight = self.get_weight_edge(
                edge, get_weight_by_map_id_func, weight_by_map_id
            )
            child_path, child_weight = self.get_best_path(
                edge.m_to,
                visited_map_ids.copy(),
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

        memo[(vertice, depth_remaining)] = max_weight

        return best_path, max_weight


if __name__ == "__main__":
    grid_signals = GridSignals()
    game_info_signals = GameInfoSignals()
    game_state = StateFactory.create_game_state(
        game_info_signals, grid_signals, logger=Logger(LogSignals())
    )
    world_signals = WorldSignals()

    start_map_id = 157704
    data_map = DataReader().map_pos_by_map_id[start_map_id]
    start_mp = MapPoint.from_cell_id(340)
    linked_zone = get_linked_zone_rp(map_id=start_map_id, cell_id=start_mp.cell_id)
    vertex = WorldGraphReader().get_vertex(start_map_id, linked_zone)

    application = QApplication(sys.argv)

    widget = MapWorldView(world_signals)

    widget.show()

    map_ids: set[int] = set()
    for sub_area_id in DataReader().sub_areas_by_area_id[
        DataReader().sub_area_by_id[data_map.subAreaId].areaId
    ]:
        map_ids |= set(DataReader().sub_area_by_id[sub_area_id].mapIds)

    add_weight = {}
    for map_id in map_ids:
        add_weight[map_id] = get_map_id_collectable_weight(
            map_id, get_gfx_to_item_and_job(), {}, {}
        )

    weighted_path = WeightedPath(game_state=game_state)

    max_weight = max(add_weight.values())

    def get_weight(map_id: int):
        map_data = DataReader().map_pos_by_map_id[map_id]
        weight = add_weight.get(map_id, -1)
        weight_color = int(255 * (weight / max_weight))
        world_signals.color_pos.emit(map_data, (255, 255 - weight_color, 0))
        return weight

    before = perf_counter()
    path, weight = weighted_path.get_best_path(
        vertex, set(), get_weight, {}, [], {}, depth_remaining=30
    )
    print(len(path))
    print(weight)
    print(perf_counter() - before)
    path_map_ids = [edge.m_to.m_mapId for edge in path]
    print(len(path_map_ids) - len(set(path_map_ids)))
    draw_edge_path(world_signals, path)
    # path = weighted_path.dfs_dynamic_max_weight(vertex, 100, {}, add_weight)

    application.exec()
