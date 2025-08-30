import math

from base_python.cache import cache
from dofus_unity_reader.data_center.data_reader import DataReader
from dofus_unity_reader.game_constants.map_id import (
    MAP_PIXEL_HALF_HEIGHT,
    MAP_PIXEL_HALF_WIDTH,
)
from dofus_unity_reader.game_constants.directions import DirectionsEnum
from dofus_unity_reader.grid.consts import (
    MAP_GRID_WIDTH,
)
from dofus_unity_reader.grid.map_point import MAP_POINT_BY_COORD, MapPoint
from dofus_unity_reader.models.maps import Transform


class MapTools:
    @staticmethod
    @cache
    def get_distance(cell_1_id: int, cell_2_id: int) -> int:
        x1 = cell_1_id % MAP_GRID_WIDTH
        y1 = (cell_1_id // MAP_GRID_WIDTH + 1) // 2 + x1
        y2 = cell_1_id // MAP_GRID_WIDTH - x1

        x2 = cell_2_id % MAP_GRID_WIDTH
        y3 = (cell_2_id // MAP_GRID_WIDTH + 1) // 2 + x2
        y4 = cell_2_id // MAP_GRID_WIDTH - x2

        return math.floor(abs(y3 - y1) + abs(y4 - y2))

    @staticmethod
    @cache
    def get_look_direction8_exact(cell_id: int, dst_cell_id: int) -> DirectionsEnum:
        _loc3_: int = math.floor(cell_id / MAP_GRID_WIDTH)
        _loc4_: int = math.floor((_loc3_ + 1) / 2)
        _loc5_ = cell_id - _loc3_ * MAP_GRID_WIDTH
        _loc6_: int = math.floor(cell_id / MAP_GRID_WIDTH)
        _loc7_: int = math.floor((_loc6_ + 1) / 2)
        _loc8_ = _loc6_ - _loc7_
        _loc9_ = cell_id - _loc6_ * MAP_GRID_WIDTH
        _loc10_: int = math.floor(dst_cell_id / MAP_GRID_WIDTH)
        _loc11_: int = math.floor((_loc10_ + 1) / 2)
        _loc12_ = dst_cell_id - _loc10_ * MAP_GRID_WIDTH
        _loc13_: int = math.floor(dst_cell_id / MAP_GRID_WIDTH)
        _loc14_: int = math.floor((_loc13_ + 1) / 2)
        _loc15_ = _loc13_ - _loc14_
        _loc16_ = dst_cell_id - _loc13_ * MAP_GRID_WIDTH
        look_direction = MapTools.get_look_direction8_exact_by_coord(
            _loc4_ + _loc5_, _loc9_ - _loc8_, _loc11_ + _loc12_, _loc16_ - _loc15_
        )
        if look_direction is None:
            raise ValueError(f"look direction should not be none ? {cell_id} -> {dst_cell_id}")
        return look_direction

    @staticmethod
    def get_look_direction8_exact_by_coord(x_1: int, y_1: int, x_2: int, y_2: int) -> DirectionsEnum | None:
        look_direction = MapTools.get_look_direction4_exact_by_coord(x_1, y_1, x_2, y_2)
        if look_direction is None:
            look_direction = MapTools.get_look_direction4_diag_exact_by_coord(x_1, y_1, x_2, y_2)
        return look_direction

    @staticmethod
    def get_look_direction4_exact_by_coord(x_1: int, y_1: int, x_2: int, y_2: int) -> DirectionsEnum | None:
        diff_x = x_2 - x_1
        diff_y = y_2 - y_1
        if diff_y == 0:
            if diff_x < 0:
                return DirectionsEnum(5)
            return DirectionsEnum(1)
        if diff_x == 0:
            if diff_y < 0:
                return DirectionsEnum(3)
            return DirectionsEnum(7)
        return None

    @staticmethod
    def get_look_direction4_diag_exact_by_coord(
        x_1: int, y_1: int, x_2: int, y_2: int
    ) -> DirectionsEnum | None:
        diff_x = x_2 - x_1
        diff_y = y_2 - y_1
        if diff_x == -diff_y:
            if diff_x < 0:
                return DirectionsEnum(6)
            return DirectionsEnum(2)
        if diff_x == diff_y:
            if diff_x < 0:
                return DirectionsEnum(4)
            return DirectionsEnum(0)
        return None

    @staticmethod
    @cache
    def get_mps_between(mp1: MapPoint, mp2: MapPoint) -> list[MapPoint]:
        precision = 0.0001
        if mp1 == mp2:
            return []

        mp1_x = mp1.x
        mp1_y = mp1.y
        mp2_x = mp2.x
        mp2_y = mp2.y

        x_diff = mp2_x - mp1_x
        y_diff = mp2_y - mp1_y
        square_dist = math.sqrt(x_diff * x_diff + y_diff * y_diff)

        nx_diff = x_diff / square_dist
        x_step = abs(1 / nx_diff) if nx_diff != 0 else float("inf")
        x_dir = -1 if nx_diff < 0 else 1
        curr_x = 0.5 * x_step

        ny_diff = y_diff / square_dist
        y_step = abs(1 / ny_diff) if ny_diff != 0 else float("inf")
        y_dir = -1 if ny_diff < 0 else 1
        curr_y = 0.5 * y_step

        result: list[MapPoint] = []
        while mp1_x != mp2_x or mp1_y != mp2_y:
            if abs(curr_x - curr_y) < precision:
                curr_x += x_step
                curr_y += y_step
                mp1_x += x_dir
                mp1_y += y_dir

            elif curr_x < curr_y:
                curr_x += x_step
                mp1_x += x_dir

            else:
                curr_y += y_step
                mp1_y += y_dir

            related_mp = MAP_POINT_BY_COORD.get((mp1_x, mp1_y))
            if related_mp is None:
                continue
            result.append(related_mp)

        return result

    @staticmethod
    def is_transform_outside_map(transform: Transform) -> bool:
        m31 = transform.m31
        m32 = transform.m32
        return abs(m31) > MAP_PIXEL_HALF_WIDTH or abs(m32) > MAP_PIXEL_HALF_HEIGHT

    @staticmethod
    def is_map_allowed_for_unsub(map_id: int) -> bool:
        return (
            DataReader().sub_area_by_id[DataReader().map_info_by_map_id[map_id].subAreaId].basicAccountAllowed
        ) == 1
