from D3Database.data_center.data_reader import DataReader
from D3Database.enums.area_enum import AreaEnum
from D3Database.models.datas.map_positions_root import MapPositionsRootItem
from src.core.engine.movements.waypoint_info import WaypointInfoNode
from src.core.engine.movements.world.map_position import get_dist_to_maps

ADDITIONAL_WEIGHT_WAYPOINT = 2


def get_near_waypoint(
    available_waypoint_map_ids: list[int],
    dist_player_to_ends: float | None,
    ends_pos: list[MapPositionsRootItem],
    check_owned: bool,
):
    near_waypoint: WaypointInfoNode | None = None

    for waypoint in DataReader().waypoint_by_id.values():
        if waypoint.activated == 0:
            continue
        if check_owned and waypoint.mapId not in available_waypoint_map_ids:
            continue
        map_waypoint_pos = DataReader().map_pos_by_map_id[waypoint.mapId]
        if (
            DataReader().sub_area_by_id[map_waypoint_pos.subAreaId].areaId
            == AreaEnum.INCARNAM
        ):
            continue

        dist_waypoint = get_dist_to_maps(map_waypoint_pos, ends_pos)
        if (
            dist_player_to_ends is not None
            and (dist_waypoint + ADDITIONAL_WEIGHT_WAYPOINT) >= dist_player_to_ends
        ):
            continue

        if near_waypoint is None or near_waypoint.dist_to_target > dist_waypoint:
            near_waypoint = WaypointInfoNode(
                map_id=waypoint.mapId,
                map_position=map_waypoint_pos,
                dist_to_target=dist_waypoint,
            )

    return near_waypoint
