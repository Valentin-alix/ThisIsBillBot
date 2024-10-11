import math
from dataclasses import dataclass
from functools import cached_property
from typing import Any

from src.common.cache import cache
from src.core.logic.grid.consts import MAP_WIDTH, MAP_HEIGHT, CELL_WIDTH, CELL_HEIGHT
from src.core.logic.grid.directions import DirectionsEnum


def get_map_point_by_cell_id_and_by_coord() -> (
    tuple[dict[int, "MapPoint"], dict[tuple[int, int], "MapPoint"]]
):
    map_point_by_id: dict[int, MapPoint] = {}
    map_point_by_coord: dict[tuple[int, int], MapPoint] = {}
    start_x: int = 0
    start_y: int = 0
    cell_index: int = 0

    pixel_x: float
    pixel_y: float
    for row in range(MAP_HEIGHT):
        for col in range(MAP_WIDTH):
            pixel_x = col * CELL_WIDTH
            pixel_y = row * CELL_HEIGHT

            x, y = start_x + col, start_y + col
            map_point = MapPoint(
                x=x, y=y, pixel_coord=(pixel_x, pixel_y), cell_id=cell_index
            )
            map_point_by_id[cell_index] = map_point
            map_point_by_coord[(x, y)] = map_point
            cell_index += 1

        start_x += 1

        for col in range(MAP_WIDTH):
            pixel_x = (col + 0.5) * CELL_WIDTH
            pixel_y = (row + 0.5) * CELL_HEIGHT
            x, y = start_x + col, start_y + col
            map_point = MapPoint(
                x=x, y=y, pixel_coord=(pixel_x, pixel_y), cell_id=cell_index
            )
            map_point_by_id[cell_index] = map_point
            map_point_by_coord[(x, y)] = map_point
            cell_index += 1

        start_y -= 1

    return map_point_by_id, map_point_by_coord


@dataclass(frozen=True)
class MapPoint:
    cell_id: int
    x: int
    y: int
    pixel_coord: tuple[float, float]

    def __str__(self):
        return f"cell_id={self.cell_id} x={self.x} y={self.y}"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other: Any):
        if type(other) is not MapPoint:
            return False
        return self.cell_id == other.cell_id

    def __hash__(self):
        return self.cell_id.__hash__()

    @staticmethod
    def from_coords(x: int, y: int) -> "MapPoint":
        return MAP_POINT_BY_COORD[(x, y)]

    @staticmethod
    def from_cell_id(cell_id: int) -> "MapPoint":
        return MAP_POINT_BY_CELL_ID[cell_id]

    @cached_property
    def side_map_points(self) -> set["MapPoint"]:
        """get the four point next to this point (not in diag)"""
        side_map_points: set[MapPoint] = set()
        coords = [
            (self.x + 1, self.y),
            (self.x, self.y + 1),
            (self.x - 1, self.y),
            (self.x, self.y - 1),
        ]
        for coord in coords:
            if coord not in MAP_POINT_BY_COORD:
                continue
            side_map_points.add(self.from_coords(*coord))
        return side_map_points

    @cache
    def distance_to_map_point(self, map_point: "MapPoint") -> float:
        return abs(self.x - map_point.x) + abs(self.y - map_point.y)

    def is_diagonal_move(self, map_point: "MapPoint") -> bool:
        return not (self.y == map_point.y or self.x == map_point.x)

    def advanced_orientation_to(
        self, target: "MapPoint", four_dir: bool = True
    ) -> DirectionsEnum:
        xdiff = target.x - self.x
        ydiff = self.y - target.y

        angle = (
            math.acos(xdiff / max(math.sqrt(xdiff**2 + ydiff**2), 1))
            * 180
            / math.pi
            * (-1 if target.y > self.y else 1)
        )
        if four_dir:
            angle = round(angle / 90) * 2 + 1
        else:
            angle = round(angle / 45) + 1

        if angle < 0:
            angle += 8

        return DirectionsEnum(int(angle))

    def orientation_to(self, mp: "MapPoint") -> DirectionsEnum:
        if self.x == mp.x and self.y == mp.y:
            return DirectionsEnum.DOWN_RIGHT

        x = 1 if mp.x > self.x else (-1 if mp.x < self.x else 0)
        y = 1 if mp.y > self.y else (-1 if mp.y < self.y else 0)

        orientation = DirectionsEnum.RIGHT

        if x == 1 and y == 1:
            orientation = DirectionsEnum.RIGHT

        elif x == 1 and y == 0:
            orientation = DirectionsEnum.DOWN_RIGHT

        elif x == 1 and y == -1:
            orientation = DirectionsEnum.DOWN

        elif x == 0 and y == -1:
            orientation = DirectionsEnum.DOWN_LEFT

        elif x == -1 and y == -1:
            orientation = DirectionsEnum.LEFT

        elif x == -1 and y == 0:
            orientation = DirectionsEnum.UP_LEFT

        elif x == -1 and y == 1:
            orientation = DirectionsEnum.UP

        elif x == 0 and y == 1:
            orientation = DirectionsEnum.UP_RIGHT

        return orientation

    def get_nearest_mp_in_direction(
        self, direction: DirectionsEnum
    ) -> "MapPoint | None":
        match direction:
            case DirectionsEnum.RIGHT:
                coord = self.x + 1, self.y + 1
            case DirectionsEnum.DOWN_RIGHT:
                coord = self.x + 1, self.y
            case DirectionsEnum.DOWN:
                coord = self.x + 1, self.y - 1
            case DirectionsEnum.DOWN_LEFT:
                coord = self.x, self.y - 1
            case DirectionsEnum.LEFT:
                coord = self.x - 1, self.y - 1
            case DirectionsEnum.UP_LEFT:
                coord = self.x - 1, self.y
            case DirectionsEnum.UP:
                coord = self.x - 1, self.y + 1
            case DirectionsEnum.UP_RIGHT:
                coord = self.x, self.y + 1
            case _:
                raise ValueError(f"invalid orientation : {direction}")
        if coord in MAP_POINT_BY_COORD:
            return MapPoint.from_coords(*coord)
        return None


MAP_POINT_BY_CELL_ID, MAP_POINT_BY_COORD = get_map_point_by_cell_id_and_by_coord()


if __name__ == "__main__":
    print(MapPoint.from_coords(15, -2))
    # cells = [484, 485, 513, 512]
    # for cell in cells:
    #     print(MapPoint.from_cell_id(cell))
