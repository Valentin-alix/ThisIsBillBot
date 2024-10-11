import sys
from dataclasses import dataclass
from threading import Thread
from time import sleep
from typing import Iterator

from PyQt5.QtWidgets import QApplication

from models.world_graph import Vertice
from src.core.data_center.data_reader import DataReader
from src.core.data_center.world_graph_reader import WorldGraphReader
from src.core.logic.grid.map_point import MapPoint
from src.core.logic.world.astar_world import AstarWorld
from src.core.logic.world.edge import (
    iter_valid_outgoing_edges,
)
from src.core.logic.world.linked_zone import get_linked_zone_rp
from src.core.states.state_factory import StateFactory
from src.gui.components.graphics.map_world_widget import MapWorldView
from src.interfaces.enums.transition_type import TransitionTypeEnum
from src.signals.grid_signals import GridSignals
from src.signals.player_signals import GameInfoSignals
from src.signals.world_signals import WorldSignals


@dataclass
class AstarNoInteractive(AstarWorld):
    def get_neighbors(self, vertice: Vertice) -> Iterator[Vertice]:
        if self.world_signals:
            map_data = DataReader().map_pos_by_map_id[vertice.m_mapId]
            self.world_signals.color_pos.emit(map_data, (0, 255, 0))
            sleep(0.01)

        for edge in iter_valid_outgoing_edges(vertice, game_state=self.game_state):
            transition_type = edge.m_transitions[0].m_type
            if transition_type not in [
                TransitionTypeEnum.MAP_ACTION,
                TransitionTypeEnum.SCROLL_ACTION,
                TransitionTypeEnum.SCROLL,
            ]:
                continue
            yield edge.m_to


if __name__ == "__main__":
    debug_world_signals = WorldSignals()
    grid_signals = GridSignals()
    game_info_signals = GameInfoSignals()
    game_state = StateFactory.create_game_state(
        game_info_signals=game_info_signals, grid_signals=grid_signals
    )
    application = QApplication(sys.argv)

    widget = MapWorldView(debug_world_signals)

    start = MapPoint.from_cell_id(298)
    map_id = 190840833
    linked_zone = get_linked_zone_rp(map_id=map_id, cell_id=start.cell_id)
    vertex = WorldGraphReader().get_vertex(map_id, linked_zone)
    game_state.map.map_id = map_id

    map_dst = 193463296
    dst_vertex = WorldGraphReader().get_vertex(map_dst, linked_zone)

    debug_world_signals.color_pos.emit(
        DataReader().map_pos_by_map_id[map_id], (255, 0, 0)
    )
    debug_world_signals.color_pos.emit(
        DataReader().map_pos_by_map_id[map_dst], (255, 0, 0)
    )
    widget.show()

    astar_world = AstarNoInteractive(
        game_state=game_state, world_signals=debug_world_signals
    )

    def _find_path():
        res = astar_world.find_path(start=vertex, ends={dst_vertex})
        print(res)

    thread = Thread(target=_find_path, daemon=True)
    thread.start()

    application.exec()
