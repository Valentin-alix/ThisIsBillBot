import sys
from dataclasses import dataclass
from time import perf_counter

from PyQt5.QtWidgets import QApplication

from models.world_graph import Vertice, Edge
from src.core.data_center.data_reader import DataReader
from src.core.data_center.i18n import I18N
from src.core.data_center.world_graph_reader import WorldGraphReader
from src.core.logic.farmer.weight_collectables import get_additional_weight_by_map_id
from src.core.logic.grid.map_point import MapPoint
from src.core.logic.world.edge import (
    iter_valid_outgoing_edges,
)
from src.core.logic.world.linked_zone import get_linked_zone_rp
from src.core.states.game_state import GameState
from src.core.states.state_factory import StateFactory
from src.gui.components.graphics.map_world_widget import MapWorldView
from src.signals.grid_signals import GridSignals
from src.signals.player_signals import GameInfoSignals
from src.signals.world_signals import WorldSignals


@dataclass
class WeightedPath:
    game_state: GameState

    def find_best_edge(
        self,
        vertice: Vertice,
        weight_by_map_id: dict[int, float],
        depth: int = 12,
    ) -> Edge | None:
        path = self.get_best_path(
            vertice=vertice,
            depth=depth,
            visited_vertice_uid=set(),
            current_path=[],
            weight_by_map_id=weight_by_map_id,
        )[0]
        if len(path) == 0:
            return None

        return path[0]

    def get_best_path(
        self,
        vertice: Vertice,
        visited_vertice_uid: set[int],
        weight_by_map_id: dict[int, float],
        current_path: list[Edge],
        curr_weight: float = 0,
        depth: int = 12,
    ) -> tuple[list[Edge], float]:

        if depth == 0:
            return current_path, curr_weight

        visited_vertice_uid.add(vertice.m_mapId)
        max_weight = curr_weight
        best_path = current_path

        for edge in iter_valid_outgoing_edges(vertice, game_state=self.game_state):
            if edge.m_to.m_mapId in visited_vertice_uid:
                continue
            weight = weight_by_map_id.get(edge.m_to.m_mapId, 0)

            child_curr_path = current_path[::]
            child_curr_path.append(edge)

            child_path, child_weight = self.get_best_path(
                edge.m_to,
                visited_vertice_uid.copy(),
                weight_by_map_id,
                current_path=child_curr_path,
                curr_weight=curr_weight + weight,
                depth=depth - 1,
            )
            if child_weight > max_weight:
                max_weight = child_weight
                best_path = child_path

        return best_path, max_weight


if __name__ == "__main__":
    grid_signals = GridSignals()
    game_info_signals = GameInfoSignals()
    game_state = StateFactory.create_game_state(game_info_signals, grid_signals)
    world_signals = WorldSignals()

    start_map_id = 189530112
    data_map = DataReader().map_pos_by_map_id[start_map_id]
    start_mp = MapPoint.from_cell_id(350)
    linked_zone = get_linked_zone_rp(map_id=start_map_id, cell_id=start_mp.cell_id)
    vertex = WorldGraphReader().get_vertex(start_map_id, linked_zone)

    application = QApplication(sys.argv)

    widget = MapWorldView(world_signals)

    widget.show()

    sub_area = DataReader().sub_area_by_id[97]
    map_ids = sub_area.mapIds
    print(I18N().name_by_id[sub_area.nameId])

    add_weight = get_additional_weight_by_map_id(set(map_ids), {})

    max_weight = max(add_weight.values())

    for map_id, weight in add_weight.items():
        weight_color = int(255 * (weight / max_weight))
        map_data = DataReader().map_pos_by_map_id[map_id]
        world_signals.color_pos.emit(map_data, (255 - weight_color, 255, 0))

    for map_id, weight in add_weight.items():
        weight_color = int(255 * (weight / max_weight))
        map_data = DataReader().map_pos_by_map_id[map_id]
        world_signals.color_pos.emit(map_data, (255 - weight_color, 255, 0))

    weighted_path = WeightedPath(game_state=game_state)
    before = perf_counter()
    next_edge = weighted_path.find_best_edge(
        vertice=vertex, weight_by_map_id=add_weight
    )
    if next_edge:
        map_pos = DataReader().map_pos_by_map_id[next_edge.m_to.m_mapId]
        print(map_pos)
    print(perf_counter() - before)

    application.exec()
