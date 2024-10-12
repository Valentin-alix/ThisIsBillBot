import sys
from dataclasses import dataclass
from threading import Thread

from PyQt5.QtWidgets import QApplication

from models.world_graph import Vertice, Edge
from src.common.logger import Logger
from src.core.data_center.data_reader import DataReader
from src.core.data_center.world_graph_reader import WorldGraphReader
from src.core.logic.grid.data_map_provider import DataMapProvider
from src.core.logic.grid.map_point import MapPoint
from src.core.logic.grid.path_finding.path_finding import Pathfinding
from src.core.logic.world.astar_vertice import AstarWorld
from src.core.logic.world.linked_zone import get_linked_zone_rp
from src.core.states.game_state import GameState
from src.core.states.state_factory import StateFactory
from src.gui.components.graphics.map_world_widget import MapWorldView
from src.signals.grid_signals import GridSignals
from src.signals.log_signals import LogSignals
from src.signals.player_signals import GameInfoSignals
from src.signals.world_signals import WorldSignals


@dataclass
class WorldPathFinder:
    path_finding: Pathfinding
    game_state: GameState

    astar_world: AstarWorld

    def find_path(
        self, src_vertex: Vertice, dst_map_ids: set[int], linked_zone: int | None = None
    ) -> list[Edge] | None:

        dst_vertexes: set[Vertice]
        if linked_zone is not None:
            dst_vertexes = {
                vertex
                for dst_map_id in dst_map_ids
                if (vertex := WorldGraphReader().get_vertex(dst_map_id, linked_zone))
                is not None
            }
        else:
            dst_vertexes = {
                vertex
                for dst_map_id in dst_map_ids
                for vertex in WorldGraphReader().get_vertexes(dst_map_id)
            }

        if src_vertex in dst_vertexes:
            return []

        if len(dst_vertexes) == 0:
            return None
        path = self.astar_world.find_path(start=src_vertex, ends=dst_vertexes)
        return path


if __name__ == "__main__":
    grid_signals = GridSignals()
    game_info_signals = GameInfoSignals()
    debug_world_signals = WorldSignals()
    logger = Logger(LogSignals())
    game_state = StateFactory.create_game_state(
        game_info_signals, grid_signals, logger=logger
    )
    data_map_provider = DataMapProvider(game_state=game_state)
    path_finding = Pathfinding(
        data_map_provider=data_map_provider, game_state=game_state, logger=logger
    )
    astar_world = AstarWorld(world_signals=debug_world_signals, game_state=game_state)
    auto_trip = WorldPathFinder(
        path_finding=path_finding, game_state=game_state, astar_world=astar_world
    )

    map_id = 120062979
    map_start_pos = DataReader().map_pos_by_map_id[map_id]
    print(map_start_pos.posX, map_start_pos.posY)
    start = MapPoint.from_cell_id(175)
    is_in_fight = False
    game_state.map.map_id = map_id
    linked_zone = get_linked_zone_rp(map_id=map_id, cell_id=start.cell_id)
    vertex = WorldGraphReader().get_vertex(map_id, linked_zone)

    map_dst = {207619076}

    application = QApplication(sys.argv)
    widget = MapWorldView(debug_world_signals)
    debug_world_signals.color_pos.emit(map_start_pos, (0, 255, 255))
    for map_id in map_dst:
        map_pos = DataReader().map_pos_by_map_id[map_id]
        print(map_pos.posX, map_pos.posY)
        debug_world_signals.color_pos.emit(map_pos, (255, 0, 0))
    widget.show()

    def _find_path():
        res = auto_trip.find_path(vertex, dst_map_ids=map_dst)
        print(res)

    thread = Thread(target=_find_path, daemon=True)
    thread.start()

    application.exec()
