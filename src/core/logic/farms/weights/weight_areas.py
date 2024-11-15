from time import perf_counter

from d3_mapping.resources.protos.game.common_pb2 import ObjectItemInventory
from data_center.data_reader import DataReader
from data_center.i18n import I18N
from enums.jobs_enum import JobEnum

from src.controller.sale_hotel import SaleHotelController
from src.core.config.auto import AREAS_SUB_WITH_WEIGHT
from src.core.logic.farms.weights.weight_items import (
    get_map_id_collectable_weight,
)


def get_weight_area(
    job_lvl_by_id: dict[int, int],
    area_id: int,
    is_sub: bool,
    storage_by_gid: dict[int, ObjectItemInventory],
):
    return sum(
        [
            get_weight_sub_area(job_lvl_by_id, storage_by_gid, sub_area_id, is_sub)
            for sub_area_id in DataReader().sub_areas_by_area_id[area_id]
        ]
    )


def get_weight_sub_area(
    job_lvl_by_id: dict[int, int],
    storage_by_gid: dict[int, ObjectItemInventory],
    sub_area_id: int,
    is_sub: bool,
):
    weight: float = 0
    avg_price_by_gid = SaleHotelController().get_avg_price_by_gid()
    for map_id in DataReader().map_ids_by_sub_area_id[sub_area_id]:
        weight += get_map_id_collectable_weight(
            map_id, job_lvl_by_id, storage_by_gid, avg_price_by_gid, is_sub
        )
    return int(weight / len(DataReader().map_ids_by_sub_area_id[sub_area_id]))


if __name__ == "__main__":
    job_lvl_by_id = {
        JobEnum.ALCHEMIST.value: 200,
        JobEnum.WOODCUTTER.value: 200,
        JobEnum.FISHERMAN.value: 200,
        JobEnum.PEASANT.value: 200,
        JobEnum.MINER.value: 200,
    }

    for i in range(3):
        before = perf_counter()
        for area_info in AREAS_SUB_WITH_WEIGHT:
            if area_info.sub_area_id:
                print(
                    f"{get_weight_sub_area(job_lvl_by_id, {}, area_info.sub_area_id, False)} Sub Area : {I18N().name_by_id[DataReader().sub_area_by_id[area_info.sub_area_id].nameId]}"
                )
            else:
                print(
                    f"{get_weight_area(job_lvl_by_id, area_info.area_id, False, {})} Area : {I18N().name_by_id[DataReader().area_by_id[area_info.area_id].nameId]}"
                )
        print(perf_counter() - before)
