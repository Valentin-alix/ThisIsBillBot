import math

from src.core.logic.path_finding.consts import MAX_Y_COORD, MIN_Y_COORD
from src.core.logic.path_finding.map_point import MAP_HEIGHT, MAP_WIDTH


class MapTools:
    @staticmethod
    def get_cell_x_by_id(cell_id: int) -> int:
        loc2: int = math.floor(cell_id / MAP_WIDTH)
        loc3: int = math.floor((loc2 + 1) / 2)
        loc4 = cell_id - loc2 * MAP_WIDTH
        return loc3 + loc4

    @staticmethod
    def get_cell_y_by_id(cell_id: int) -> int:
        _loc2_: int = math.floor(cell_id / MAP_WIDTH)
        _loc3_: int = math.floor((_loc2_ + 1) / 2)
        _loc4_ = _loc2_ - _loc3_
        _loc5_ = cell_id - _loc2_ * MAP_WIDTH
        return _loc5_ - _loc4_

    @staticmethod
    def get_cell_id_by_coord(x: int, y: int):
        cell_id = int((x - y) * MAP_WIDTH + y + (x - y) / 2)
        return cell_id

    @staticmethod
    def is_valid_coord(x: int, y: int) -> bool:
        if y >= -x and y <= x and y <= MAP_WIDTH + MAX_Y_COORD - x:
            return y >= x - (MAP_HEIGHT - MIN_Y_COORD)
        return False
