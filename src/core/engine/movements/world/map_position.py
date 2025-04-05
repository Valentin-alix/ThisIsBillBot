from dofus_unity_reader.data_center.data_reader import DataReader
from dofus_unity_reader.game_constants.area import AreaEnum
from dofus_unity_reader.models.datas.map_positions_root import MapInformationRootItem

from src.const import FAKE_INFINITY_VALUE


def get_dist_to_maps(
    map_pos: MapInformationRootItem, ends_pos: list[MapInformationRootItem]
) -> float:
    if DataReader().sub_area_by_id[
        map_pos.subAreaId
    ].areaId == AreaEnum.INCARNAM and not any(
        DataReader().sub_area_by_id[end_pos.subAreaId].areaId != AreaEnum.INCARNAM
        for end_pos in ends_pos
    ):
        return FAKE_INFINITY_VALUE
    dist_to_end_pos: list[float] = []
    for end_pos in ends_pos:
        manhattan_dist = abs(map_pos.posX - end_pos.posX) + abs(
            map_pos.posY - end_pos.posY
        )
        if manhattan_dist == 0 and end_pos.subAreaId != map_pos.subAreaId:
            dist = 10
        else:
            dist = manhattan_dist
        dist_to_end_pos.append(dist)
    return min(dist_to_end_pos)
