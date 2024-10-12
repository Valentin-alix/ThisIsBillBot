import math

from protos.game.common_pb2 import ObjectItemInventory
from src.core.behaviors.storage.consts import USEFUL_INGREDIENT_IDS
from src.core.data_center.data_reader import DataReader
from src.core.data_center.map_reader import MapReader
from src.core.logic.farmer.collectables import (
    get_gfx_to_item_and_job,
    get_collectable_map_checked,
)
from src.core.logic.grid.map_tools import MapTools
from src.interfaces.enums.job_enum import JobEnum
from src.signals.world_signals import WorldSignals

WEIGHT_BY_JOB: dict[JobEnum, float] = {
    JobEnum.MINER: 50,
    JobEnum.WOODCUTTER: 30,
    JobEnum.ALCHEMIST: 10,
    JobEnum.PEASANT: 10,
    JobEnum.FISHERMAN: 10,
    JobEnum.BASE: 1,
}


def get_map_id_collectable_weight(
    map_id: int,
    gfx_to_item_and_job: dict[int, tuple[int, JobEnum]],
    player_job_lvl_by_id: dict[int, int],
    storage_by_gid: dict[int, ObjectItemInventory],
) -> float:
    weight_map: float = 0
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
        job_lvl = player_job_lvl_by_id.get(job_id, 1)
        if item.level > job_lvl:
            continue
        weight_item = (
            WEIGHT_BY_JOB[job_id]
            * item.level
            * (3 if item.id in USEFUL_INGREDIENT_IDS else 1)
            / (
                max(math.log(storage_by_gid[item.id].item.quantity / 1000), 0.1)
                if item.id in storage_by_gid and storage_by_gid.get(item.id, 0) != 0
                else 0.1
            )
        )
        weight_item *= ((201 - job_lvl) / 2) if job_id != JobEnum.BASE else 1
        weight_map += weight_item
    return weight_map


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
            if item not in item_knows and item in DataReader().gathered_item_ids:
                map_ids_to_check.add(map_id)
                break

    return map_ids_to_check


def draw_weight_on_map(weight_by_map_id: dict[int, float], world_signals: WorldSignals):
    if len(weight_by_map_id) == 0:
        return
    max_weight = max(weight_by_map_id.values())
    world_signals.reset_weight.emit()
    for map_id, weight in weight_by_map_id.items():
        map_data = DataReader().map_pos_by_map_id[map_id]
        weight_color = int(255 * (weight / max_weight))
        world_signals.color_pos.emit(map_data, (255, 255 - weight_color, 0))


if __name__ == "__main__":
    map_id = 54171949
    area_id = (
        DataReader()
        .sub_area_by_id[DataReader().map_pos_by_map_id[map_id].subAreaId]
        .areaId
    )

    map_ids: set[int] = set()
    for sub_area_id in DataReader().sub_areas_by_area_id[area_id]:
        if DataReader().sub_area_by_id[sub_area_id].level > 95:
            continue
        map_ids |= set(DataReader().sub_area_by_id[sub_area_id].mapIds)

    map_ids_to_explore = get_map_ids_to_explore(map_ids)

    additional_weight_by_map_id = get_additional_weight_by_map_id(
        map_ids,
        {
            JobEnum.PEASANT: 58,
            JobEnum.WOODCUTTER: 200,
            JobEnum.FISHERMAN: 200,
            JobEnum.ALCHEMIST: 200,
            JobEnum.MINER: 25,
        },
        {},
    )
    max_value = max(additional_weight_by_map_id.values())
    for map_id in map_ids_to_explore:
        # print(map_id)
        additional_weight_by_map_id[map_id] = max_value
    print(additional_weight_by_map_id)
    # print(additional_weight_by_map_id)
