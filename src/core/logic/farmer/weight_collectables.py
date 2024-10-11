import sys
from datetime import datetime
from time import perf_counter

from PyQt5.QtWidgets import QApplication

from src.const import MIN_DATE
from src.core.data_center.data_reader import DataReader
from src.core.data_center.i18n import I18N
from src.core.data_center.map_reader import MapReader
from src.core.logic.farmer.collectables import (
    get_gfx_to_item_and_job,
    get_collectable_map_checked,
)
from src.core.logic.grid.map_tools import MapTools
from src.gui.pages.farmer.world_tab import WorldTab
from src.interfaces.enums.job_enum import JobEnum
from src.signals.world_signals import WorldSignals

WEIGHT_BY_JOB: dict[JobEnum, float] = {
    JobEnum.MINER: 100,
    JobEnum.WOODCUTTER: 30,
    JobEnum.ALCHEMIST: 10,
    JobEnum.PEASANT: 1,
    JobEnum.FISHERMAN: 1,
    JobEnum.BASE: 1,
}


def get_additional_weight_by_map_id(
    map_ids: set[int], player_job_lvl_by_id: dict[int, int]
) -> dict[int, float]:
    additional_weight_by_map_id: dict[int, float] = {}
    gfx_to_item_and_job = get_gfx_to_item_and_job()
    for map_id in map_ids:
        weight_map: float = 1
        for ref_id in MapReader().map_by_id(map_id).references:
            if ref_id.transform is None:
                continue
            if MapTools.is_transform_outside_map(ref_id.transform):
                continue
            info = gfx_to_item_and_job.get(ref_id.gfxId)
            if info is None:
                continue
            item_id, job_id = info
            item = DataReader().item_by_id[item_id]
            if item.level > player_job_lvl_by_id.get(job_id, 1):
                continue
            weight_map += WEIGHT_BY_JOB[job_id] * item.level
        additional_weight_by_map_id[map_id] = weight_map

    return additional_weight_by_map_id


def get_map_ids_to_explore(map_ids: set[int]) -> set[int]:
    map_ids_to_check: set[int] = set()

    map_id_checked: set[int] = get_collectable_map_checked()
    item_knows = set((item_id for item_id, _ in get_gfx_to_item_and_job().values()))

    for map_id in map_ids:
        if map_id in map_id_checked:
            continue
        sub_area = DataReader().map_pos_by_map_id[map_id].subAreaId
        harvestable_items_sub_area = DataReader().sub_area_by_id[sub_area].harvestables
        for item in harvestable_items_sub_area:
            if item not in item_knows:
                map_ids_to_check.add(map_id)
                break

    return map_ids_to_check


def draw_weight_on_map(weight_by_map_id: dict[int, float], world_signals: WorldSignals):
    max_weight = max(weight_by_map_id.values())
    world_signals.reset_weight.emit()
    for map_id, weight in weight_by_map_id.items():
        map_data = DataReader().map_pos_by_map_id[map_id]
        weight_color = int(255 * (weight / max_weight))
        world_signals.color_pos.emit(map_data, (255, 255 - weight_color, 0))


def temp_weight(
    last_visited_by_map_id: dict[int, datetime],
    additional_weight_by_map_id: dict[int, float],
    map_id: int,
) -> float:
    last_visited = last_visited_by_map_id.get(map_id, MIN_DATE)
    return (
        min((datetime.now() - last_visited).total_seconds(), 1800) / 5
    ) * additional_weight_by_map_id.get(map_id, 1)


if __name__ == "__main__":
    world_signals = WorldSignals()

    application = QApplication(sys.argv)

    widget = WorldTab(world_signals)
    widget.show()

    sub_area_id = DataReader().map_pos_by_map_id[190842370].subAreaId
    sub_area = DataReader().sub_area_by_id[sub_area_id]
    print(I18N().name_by_id[sub_area.nameId])

    map_ids = sub_area.mapIds

    world_signals.curr_map_pos.emit(DataReader().map_pos_by_map_id[190842370])

    add_weight = get_additional_weight_by_map_id(set(map_ids), {})

    before = perf_counter()
    weight_by_map_id: dict[int, float] = {}
    for map_id in map_ids:
        weight_by_map_id[map_id] = temp_weight(
            last_visited_by_map_id={},
            additional_weight_by_map_id=add_weight,
            map_id=map_id,
        )
    draw_weight_on_map(weight_by_map_id, world_signals)
    print(perf_counter() - before)

    # def temp():
    #     world_signals.curr_map_pos.emit(DataReader().map_pos_by_coord[(-3, -10)][0])
    #
    # timer = Timer(5, temp)
    # timer.start()

    application.exec()
