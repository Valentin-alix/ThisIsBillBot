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


if __name__ == "__main__":
    map_ids: set[int] = set()
    target_map = DataReader().map_pos_by_map_id[126224149]
    map_ids |= set(DataReader().sub_area_by_id[target_map.subAreaId].mapIds)

    curr_map_pos = DataReader().map_pos_by_map_id[147590153]
    print(curr_map_pos.posX, curr_map_pos.posY)
    dst_map_pos = [DataReader().map_pos_by_map_id[map_id] for map_id in map_ids]
    dist = get_dist_to_maps(curr_map_pos, dst_map_pos)
    print(dist)
