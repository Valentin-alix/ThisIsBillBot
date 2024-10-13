import sys
from threading import Thread

from PyQt5.QtWidgets import QApplication
from src.core.data_center.data_reader import DataReader
from src.core.data_center.world_graph_reader import WorldGraphReader
from src.gui.components.graphics.map_world_widget import MapWorldView
from tests.setup_factory import GameStateFixture


class TestWorldPathFinder(GameStateFixture):
    def test_world_path_finder(self):
        self.set_game_state(175, [], map_id=120062979)
        linked_zone = self.game_state.player.linked_zone_rp
        curr_map_id = self.game_state.map.map_id
        curr_map_data = DataReader().map_pos_by_map_id[curr_map_id]
        vertex = WorldGraphReader().get_vertex(curr_map_id, linked_zone)
        assert vertex is not None

        map_dst = {207619076}
        application = QApplication(sys.argv)
        self.world_signals.color_pos.emit(curr_map_data, (0, 255, 255))
        for map_id in map_dst:
            map_pos = DataReader().map_pos_by_map_id[map_id]
            self.world_signals.color_pos.emit(map_pos, (255, 0, 0))

        self.map_world_view = MapWorldView(self.world_signals)
        self.map_world_view.show()

        def _find_path():
            res = self.world_path_finder.find_path(vertex, dst_map_ids=map_dst)
            print(res)

        thread = Thread(target=_find_path, daemon=True)
        thread.start()

        application.exec()
