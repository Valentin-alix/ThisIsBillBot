import math
from dataclasses import dataclass
from typing import Any

from src.core.logic.grid.consts import MAP_WIDTH
from src.core.logic.grid.directions import DirectionsEnum
from src.core.logic.grid.point import Point


@dataclass(frozen=True)
class MapPoint:
    cell_id: int
    point: Point

    def __eq__(self, other: Any):
        if type(other) is not MapPoint:
            return False
        return self.cell_id == other.cell_id

    def __hash__(self):
        return self.cell_id.__hash__()

    @staticmethod
    def from_cell_id(cell_id: int) -> "MapPoint":
        return MapPoint(cell_id, Point.from_cell_id(cell_id))

    @staticmethod
    def from_coords(x: int, y: int) -> "MapPoint":
        cell_id = (x - y) * MAP_WIDTH + y + (x - y) // 2
        map_point = MapPoint(cell_id, Point(x, y))
        return map_point

    def distance_to_cell_id(self, cell_id: int) -> float:
        return self.point.distance_to_point(Point.from_cell_id(cell_id))

    def advanced_orientation_to(self, target: "MapPoint", four_dir: bool = True) -> int:
        if target is None:
            return 0
        xdiff = target.point.x - self.point.x
        ydiff = target.point.y - self.point.y
        dir_count = 4 if four_dir else 8
        angle = dir_count * math.degrees(math.atan2(ydiff, xdiff)) / 360
        angle = round(angle) % dir_count + 1
        angle = (angle - 1) % 8 + 1
        return angle

    def get_nearest_mp_in_direction(
        self, direction: DirectionsEnum
    ) -> "MapPoint | None":
        match direction:
            case DirectionsEnum.RIGHT:
                mp = MapPoint.from_coords(self.point.x + 1, self.point.y + 1)
            case DirectionsEnum.DOWN_RIGHT:
                mp = MapPoint.from_coords(self.point.x + 1, self.point.y)
            case DirectionsEnum.DOWN:
                mp = MapPoint.from_coords(self.point.x + 1, self.point.y - 1)
            case DirectionsEnum.DOWN_LEFT:
                mp = MapPoint.from_coords(self.point.x, self.point.y - 1)
            case DirectionsEnum.LEFT:
                mp = MapPoint.from_coords(self.point.x - 1, self.point.y - 1)
            case DirectionsEnum.UP_LEFT:
                mp = MapPoint.from_coords(self.point.x - 1, self.point.y)
            case DirectionsEnum.UP:
                mp = MapPoint.from_coords(self.point.x - 1, self.point.y + 1)
            case DirectionsEnum.UP_RIGHT:
                mp = MapPoint.from_coords(self.point.x, self.point.y + 1)
            case _:
                raise ValueError(f"invalid orientation : {direction}")
        if mp.point.is_in_map():
            return mp
        return None
