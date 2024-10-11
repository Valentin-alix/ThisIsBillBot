import sys
from dataclasses import dataclass
from threading import Thread
from typing import Iterator

from PyQt5.QtWidgets import QApplication

from models.world_graph import Vertice, Edge
from src.common.astar import Astar, Node, T
from src.core.data_center.data_reader import DataReader
from src.core.data_center.world_graph_reader import WorldGraphReader
from src.core.logic.grid.map_point import MapPoint
from src.core.logic.world.edge import iter_valid_outgoing_edges
from src.core.logic.world.linked_zone import get_linked_zone_rp
from src.core.logic.world.map_position import get_dist_to_maps
from src.core.states.game_state import GameState
from src.core.states.state_factory import StateFactory
from src.gui.components.graphics.map_world_widget import MapWorldView
from src.signals.grid_signals import GridSignals
from src.signals.player_signals import GameInfoSignals
from src.signals.world_signals import WorldSignals


@dataclass
class AstarWorld(Astar[Vertice]):
    game_state: GameState
    world_signals: WorldSignals | None = None

    def get_neighbors(self, vertice: Vertice) -> Iterator[Vertice]:
        if self.world_signals:
            map_data = DataReader().map_pos_by_map_id[vertice.m_mapId]
            self.world_signals.color_pos.emit(map_data, (0, 255, 0))
        for edge in iter_valid_outgoing_edges(vertice, game_state=self.game_state):
            yield edge.m_to

    def get_dist(self, current: Vertice, ends: "set[Vertice]") -> float:
        curr_map_pos = DataReader().map_pos_by_map_id[current.m_mapId]
        ends_map_pos = [DataReader().map_pos_by_map_id[end.m_mapId] for end in ends]
        cost_to_ends = get_dist_to_maps(curr_map_pos, ends_map_pos)
        return cost_to_ends

    def reconstruct_path(self, node: Node[Vertice], do_reverse: bool) -> list[Edge]:
        result: list[Edge] = []
        while node.parent is not None:
            edge = WorldGraphReader().get_edge_by_src_and_dst_vertex(
                node.parent.data, node.data
            )
            result.append(edge)
            node = node.parent
        result.reverse()
        return result

    def find_path(
        self,
        start: T,
        ends: set[T],
        heuristic_scale: float = 1,
        do_reverse: bool = False,
        max_iteration: int = 9999,
    ) -> list[Edge] | None:
        return super().find_path(
            start, ends, heuristic_scale, do_reverse, max_iteration
        )


if __name__ == "__main__":
    debug_world_signals = WorldSignals()
    grid_signals = GridSignals()
    game_info_signals = GameInfoSignals()
    game_state = StateFactory.create_game_state(game_info_signals, grid_signals)

    application = QApplication(sys.argv)

    widget = MapWorldView(debug_world_signals)

    start = MapPoint.from_cell_id(114)
    map_id = 101715463
    linked_zone = get_linked_zone_rp(map_id=map_id, cell_id=start.cell_id)
    vertex = WorldGraphReader().get_vertex(map_id, linked_zone)
    game_state.map.map_id = map_id
    map_dst = 137737

    dst_vertex = WorldGraphReader().get_vertex(map_dst, linked_zone)

    debug_world_signals.color_pos.emit(
        DataReader().map_pos_by_map_id[map_id], (255, 0, 0)
    )
    debug_world_signals.color_pos.emit(
        DataReader().map_pos_by_map_id[map_dst], (255, 0, 0)
    )
    widget.show()

    astar_world = AstarWorld(game_state=game_state, world_signals=debug_world_signals)

    def _find_path():
        res = astar_world.find_path(
            start=vertex, ends={dst_vertex}, heuristic_scale=100
        )
        print(res)

    thread = Thread(target=_find_path, daemon=True)
    thread.start()

    application.exec()
