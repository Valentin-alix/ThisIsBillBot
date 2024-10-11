from models.datas.map_positions_root import MapPositionsRootItem
from src.const import FAKE_INFINITY_VALUE
from src.core.data_center.data_reader import DataReader
from src.interfaces.enums.area_enum import AreaEnum


def get_dist_to_maps(
    map_pos: MapPositionsRootItem, ends_pos: list[MapPositionsRootItem]
) -> float:
    if DataReader().sub_area_by_id[
        map_pos.subAreaId
    ].areaId == AreaEnum.INCARNAM and not any(
        DataReader().sub_area_by_id[end_pos.subAreaId].areaId != AreaEnum.INCARNAM
        for end_pos in ends_pos
    ):
        return FAKE_INFINITY_VALUE
    return min(
        abs(map_pos.posX - end_pos.posX) + abs(map_pos.posY - end_pos.posY)
        for end_pos in ends_pos
    )
