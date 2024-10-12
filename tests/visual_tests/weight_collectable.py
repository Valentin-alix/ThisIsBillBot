import sys
from threading import Thread
from time import sleep

from PyQt5.QtWidgets import QApplication

from src.core.data_center.data_reader import DataReader
from src.core.logic.farmer.weight_collectables import (
    draw_weight_on_map,
    get_additional_weight_by_map_id,
)
from src.gui.pages.farmer.world_tab import WorldTab
from src.signals.world_signals import WorldSignals


def test_weight_maps(map_id: int):
    world_signals = WorldSignals()

    application = QApplication(sys.argv)

    widget = WorldTab(world_signals)
    widget.show()

    map_ids: set[int] = set()
    sub_area_id = DataReader().map_pos_by_map_id[map_id].subAreaId
    for sub_area_id in DataReader().sub_areas_by_area_id[
        DataReader().sub_area_by_id[sub_area_id].areaId
    ]:
        map_ids |= set(DataReader().sub_area_by_id[sub_area_id].mapIds)

    world_signals.curr_map_pos.emit(DataReader().map_pos_by_map_id[map_id])

    def go_draw():
        sleep(3)
        add_weight = get_additional_weight_by_map_id(set(map_ids), {}, {})
        draw_weight_on_map(add_weight, world_signals)

    thread = Thread(target=go_draw, daemon=True)
    thread.start()

    application.exec()


if __name__ == "__main__":
    test_weight_maps(190842370)
