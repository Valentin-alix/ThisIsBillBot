import os
import random
import sys
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import Callable

from PyQt5.QtWidgets import QApplication


from src.controller.gfx_mapping import GfxMappingController

sys.path.append(
    os.path.join(Path(__file__).parent.parent.parent.parent.parent, "D3Database")
)
sys.path.append(
    os.path.join(Path(__file__).parent.parent.parent.parent.parent, "D3Mapping")
)
sys.path.append(os.path.join(Path(__file__).parent.parent.parent.parent.parent))


from data_center.data_reader import DataReader
from data_center.i18n import I18N
from data_center.world_graph_reader import WorldGraphReader
from enums.area_enum import SubAreaEnum
from grid.map_point import MapPoint
from models.world_graph import Edge, Vertice

from src.common.logger import Logger
from src.core.behaviors.storage.consts import ASTRUB_BANK_MAP
from src.core.logic.farmer.weight_collectables import (
    draw_weight_on_map,
    get_map_id_collectable_weight,
)
from src.core.logic.world.edge import (
    draw_edge_path,
    iter_valid_outgoing_edges,
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
        get_weight_by_edge_func: Callable[[Edge], float],
        weight_by_map_id: dict[int, float],
    ):
        if weight_by_map_id.get(edge.m_to.m_mapId) is None:
            weight_by_map_id[edge.m_to.m_mapId] = get_weight_by_edge_func(edge)
        return weight_by_map_id[edge.m_to.m_mapId]

    def monte_carlo_path(
        self,
        start_vertex: Vertice,
        get_weight_by_edge_func: Callable[[Edge], float],
        weight_by_map_id: dict[int, float],
        depth: int = 30,
        iterations: int = 5000,
    ):
        # heuristic, randomized weighted path
        best_score: float = 0
        best_path: list[Edge] = []

        for _ in range(iterations):
            random_depth = random.randint(5, depth)
            current_vertex = start_vertex
            visited_map_ids: list[int] = [current_vertex.m_mapId]
            total_weight: float = 0
            path: list[Edge] = []

            for _ in range(random_depth):
                edge_neighbors = [
                    neighbor
                    for neighbor in iter_valid_outgoing_edges(
                        current_vertex, self.game_state
                    )
                ]
                if not edge_neighbors:
                    break
                next_edge: Edge = random.choice(edge_neighbors)

                weight = self.get_weight_edge(
                    next_edge,
                    weight_by_map_id=weight_by_map_id,
                    get_weight_by_edge_func=get_weight_by_edge_func,
                )
                try:
                    last_visited_index = visited_map_ids.index(next_edge.m_to.m_mapId)
                    base = 0.9999
                    weight_malus = 1 - base**last_visited_index
                    weight *= weight_malus
                except ValueError:
                    pass

                path.append(next_edge)
                visited_map_ids.insert(0, next_edge.m_to.m_mapId)
                total_weight += weight
                current_vertex = next_edge.m_to

            score = total_weight / (1 + len(path) ** 0.25)
            if score > best_score:
                best_score = score
                best_path = path

        return best_path, best_score

    def get_best_path(
        self,
        vertice: Vertice,
        visited_map_ids: tuple[int, ...],
        get_weight_by_edge_func: Callable[[Edge], float],
        weight_by_map_id: dict[int, float],
        current_path: list[Edge],
        memo: dict[tuple[Vertice, int, tuple[int, ...]], float],
        curr_weight: float = 0,
        depth_remaining: int = 9,
    ) -> tuple[list[Edge], float]:
        if depth_remaining == 0:
            return current_path, curr_weight

        state = (vertice, depth_remaining, visited_map_ids[:5])
        if state in memo:
            memo_weight = memo[state]
            return current_path, memo_weight

        max_weight = curr_weight
        best_path = current_path

        for edge in iter_valid_outgoing_edges(vertice, game_state=self.game_state):
            weight = self.get_weight_edge(
                edge, get_weight_by_edge_func, weight_by_map_id
            )
            if weight is None:
                continue

            try:
                last_visited_index = visited_map_ids.index(edge.m_to.m_mapId)
                base = 0.995
                weight_malus = 1 - base**last_visited_index
                weight *= weight_malus
            except ValueError:
                pass

            child_curr_path = current_path[::]
            child_curr_path.append(edge)
            child_path, child_weight = self.get_best_path(
                edge.m_to,
                (edge.m_to.m_mapId,) + visited_map_ids,
                get_weight_by_edge_func,
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
    # init qt app
    grid_signals = GridSignals()
    game_info_signals = GameInfoSignals()
    game_state = StateFactory.create_game_state(
        game_info_signals, grid_signals, logger=Logger(LogSignals())
    )
    world_signals = WorldSignals()
    application = QApplication(sys.argv)
    widget = MapWorldView(world_signals)

    # get vertex
    start_map_id = ASTRUB_BANK_MAP
    start_mp = MapPoint.from_cell_id(340)
    start_data_map = DataReader().map_pos_by_map_id[start_map_id]
    linked_zone = get_linked_zone_rp(map_id=start_map_id, cell_id=start_mp.cell_id)
    vertex = WorldGraphReader().get_vertex(start_map_id, linked_zone)

    assert vertex

    widget.show()

    area = DataReader().area_by_id[
        DataReader().sub_area_by_id[start_data_map.subAreaId].areaId
    ]
    print(f"area : {I18N().name_by_id[area.nameId]}")

    # get all map ids in area
    # sub_areas = DataReader().sub_areas_by_area_id[area.id]
    sub_areas = [SubAreaEnum.ASTRUB_CITY]
    map_ids: set[int] = set()
    for sub_area_id in sub_areas:
        map_ids |= set(DataReader().sub_area_by_id[sub_area_id].mapIds)

    additional_weight: dict[int, float] = {}
    for map_id in map_ids:
        additional_weight[map_id] = get_map_id_collectable_weight(
            map_id, GfxMappingController().get_item_job_by_gfx(), {}, {}, {}, False
        )

    weighted_path = WeightedPath(game_state=game_state)

    max_weight = max(additional_weight.values())

    def get_weight_by_edge(edge: Edge) -> float:
        weight = additional_weight.get(edge.m_to.m_mapId, -1)
        map_data = DataReader().map_pos_by_map_id[edge.m_to.m_mapId]
        weight_color = int(255 * (weight / max_weight))
        world_signals.color_pos.emit(map_data, (255, 255 - weight_color, 0))

        return weight

    print(len(map_ids))

    before = perf_counter()

    path, weight = weighted_path.monte_carlo_path(vertex, get_weight_by_edge, {})
    print(len(path))
    print(perf_counter() - before)

    draw_weight_on_map(additional_weight, world_signals)
    draw_edge_path(world_signals, path)

    application.exec()
