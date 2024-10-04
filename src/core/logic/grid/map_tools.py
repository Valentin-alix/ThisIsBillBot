import math

from src.core.logic.grid.map_direction import MapDirection

MAP_GRID_WIDTH: int = 14
MAP_GRID_HEIGHT: int = 20
MAP_COUNT_CELL = MAP_GRID_WIDTH * MAP_GRID_HEIGHT * 2
MIN_X_COORD: int = 0
MAX_X_COORD: int = 33
MIN_Y_COORD: int = -19
MAX_Y_COORD: int = 13


class MapTools:
    @staticmethod
    def get_cell_x_by_id(cell_id: int) -> int:
        loc2: int = math.floor(cell_id / MAP_GRID_WIDTH)
        loc3: int = math.floor((loc2 + 1) / 2)
        loc4 = cell_id - loc2 * MAP_GRID_WIDTH
        return loc3 + loc4

    @staticmethod
    def get_cell_y_by_id(cell_id: int) -> int:
        _loc2_: int = math.floor(cell_id / MAP_GRID_WIDTH)
        _loc3_: int = math.floor((_loc2_ + 1) / 2)
        _loc4_ = _loc2_ - _loc3_
        _loc5_ = cell_id - _loc2_ * MAP_GRID_WIDTH
        return _loc5_ - _loc4_

    @staticmethod
    def get_cell_id_by_coord(x: int, y: int):
        cell_id = int((x - y) * MAP_GRID_WIDTH + y + (x - y) / 2)
        return cell_id

    @staticmethod
    def is_valid_coord(x: int, y: int) -> bool:
        if -x <= y <= x and y <= MAP_GRID_WIDTH + MAX_Y_COORD - x:
            return y >= x - (MAP_GRID_HEIGHT - MIN_Y_COORD)
        return False

    @staticmethod
    def is_valid_cell_id(cell_id: int) -> bool:
        if cell_id >= 0:
            return cell_id < MAP_COUNT_CELL
        return False

    @staticmethod
    def get_distance(cell_1_id: int, cell_2_id: int) -> int:
        if not MapTools.is_valid_cell_id(cell_1_id) or not MapTools.is_valid_cell_id(
            cell_2_id
        ):
            return -1
        x1 = cell_1_id % MAP_GRID_WIDTH
        y1 = (cell_1_id // MAP_GRID_WIDTH + 1) // 2 + x1
        y2 = cell_1_id // MAP_GRID_WIDTH - x1

        x2 = cell_2_id % MAP_GRID_WIDTH
        y3 = (cell_2_id // MAP_GRID_WIDTH + 1) // 2 + x2
        y4 = cell_2_id // MAP_GRID_WIDTH - x2

        return math.floor(abs(y3 - y1) + abs(y4 - y2))

    @staticmethod
    def get_look_direction4_exact_by_coord(
        param1: int, param2: int, param3: int, param4: int
    ) -> int:
        if not MapTools.is_valid_coord(param1, param2) or not MapTools.is_valid_coord(
            param3, param4
        ):
            return -1
        _loc5_ = param3 - param1
        _loc6_ = param4 - param2
        if _loc6_ == 0:
            if _loc5_ < 0:
                return 5
            return 1
        if _loc5_ == 0:
            if _loc6_ < 0:
                return 3
            return 7
        return -1

    @staticmethod
    def get_look_direction4_diag_exact_by_coord(
        param1: int, param2: int, param3: int, param4: int
    ) -> int:
        if not MapTools.is_valid_coord(param1, param2) or not MapTools.is_valid_coord(
            param3, param4
        ):
            return -1
        _loc5_ = param3 - param1
        _loc6_ = param4 - param2
        if _loc5_ == -_loc6_:
            if _loc5_ < 0:
                return 6
            return 2
        if _loc5_ == _loc6_:
            if _loc5_ < 0:
                return 4
            return 0
        return -1

    @staticmethod
    def get_look_direction8_exact_by_coord(
        param1: int, param2: int, param3: int, param4: int
    ) -> int:
        _loc5_: int = MapTools.get_look_direction4_exact_by_coord(
            param1, param2, param3, param4
        )
        if not MapDirection.is_valid_direction(_loc5_):
            _loc5_ = MapTools.get_look_direction4_diag_exact_by_coord(
                param1, param2, param3, param4
            )
        return _loc5_

    @staticmethod
    def get_look_direction8_exact(cell_id: int, dst_cell_id: int) -> int:
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
        return int(
            MapTools.get_look_direction8_exact_by_coord(
                _loc4_ + _loc5_, _loc9_ - _loc8_, _loc11_ + _loc12_, _loc16_ - _loc15_
            )
        )
