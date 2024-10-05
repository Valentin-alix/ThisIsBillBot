import math
from dataclasses import dataclass

from src.core.logic.grid.directions import DirectionsEnum
from src.core.logic.grid.map_tools import MAP_COUNT_CELL
from src.core.logic.grid.point import Point
from src.core.repositories.map_reader import MapReader

MAP_WIDTH: int = 14
MAP_HEIGHT: int = 20
VECTOR_RIGHT: Point = Point(1, 1)
VECTOR_DOWN_RIGHT: Point = Point(1, 0)
VECTOR_DOWN: Point = Point(1, -1)
VECTOR_DOWN_LEFT: Point = Point(0, -1)
VECTOR_LEFT: Point = Point(-1, -1)
VECTOR_UP_LEFT: Point = Point(-1, 0)
VECTOR_UP: Point = Point(-1, 1)
VECTOR_UP_RIGHT: Point = Point(0, 1)


def get_cell_point_by_id() -> dict[int, Point]:
    cells_pos: dict[int, Point] = {}
    start_x: int = 0
    start_y: int = 0
    cell_index: int = 0

    for _ in range(MAP_HEIGHT):
        for i_width in range(MAP_WIDTH):
            cells_pos[cell_index] = Point(start_x + i_width, start_y + i_width)
            cell_index += 1

        start_x += 1

        for i_width in range(MAP_WIDTH):
            cells_pos[cell_index] = Point(start_x + i_width, start_y + i_width)
            cell_index += 1

        start_y -= 1

    return cells_pos


CELL_POINT_BY_ID: dict[int, Point] = get_cell_point_by_id()


@dataclass
class MapPoint:
    cell_id: int
    point: Point

    def distance_to_cell_id(self, cell_id: int) -> float:
        return self.point.distance_to_point(CELL_POINT_BY_ID[cell_id])

    def allows_map_change(self, map_id: int) -> bool:
        return (
            MapReader().map_by_id(map_id).cellsData.Array[self.cell_id].mapChangeData
            != 0
        )

    @staticmethod
    def get_orientations_distance(
        current_orientation: int, default_orientation: int
    ) -> int:
        return min(
            abs(default_orientation - current_orientation),
            abs(8 - default_orientation + current_orientation),
        )

    def does_allows_map_change_to_direction(
        self, map_id: int, direction_value: int
    ) -> bool:
        cell_data = MapReader().get_ref_cell_data_by_cell_id(map_id)[self.cell_id]
        direction = DirectionsEnum(direction_value)

        map_change_data = cell_data["mapChangeData"]

        if direction == DirectionsEnum.RIGHT:
            return (
                bool(map_change_data & 1)
                or (
                    (self.cell_id + 1) % (MAP_WIDTH * 2) == 0
                    and bool(map_change_data & 2)
                )
                or (
                    (self.cell_id + 1) % (MAP_WIDTH * 2) == 0
                    and bool(map_change_data & 128)
                )
            )
        elif direction == DirectionsEnum.LEFT:
            return (
                (self.point.x == -self.point.y and bool(map_change_data & 8))
                or bool(map_change_data & 16)
                or (self.point.x == -self.point.y and bool(map_change_data & 32))
            )
        elif direction == DirectionsEnum.UP:
            return (
                (self.cell_id < MAP_WIDTH and bool(map_change_data & 32))
                or bool(map_change_data & 64)
                or (self.cell_id < MAP_WIDTH and bool(map_change_data & 128))
            )
        elif direction == DirectionsEnum.DOWN:
            return (
                (
                    self.cell_id >= MAP_COUNT_CELL - MAP_WIDTH
                    and bool(map_change_data & 2)
                )
                or bool(map_change_data & 4)
                or (
                    self.cell_id >= MAP_COUNT_CELL - MAP_WIDTH
                    and bool(map_change_data & 8)
                )
            )

        return False

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

    def get_nearest_mp_in_direction(self, orientation: int) -> "MapPoint | None":
        direction = DirectionsEnum(orientation)
        if direction == DirectionsEnum.RIGHT:
            mp = MapPoint.from_coords(self.point.x + 1, self.point.y + 1)
        elif direction == DirectionsEnum.DOWN_RIGHT:
            mp = MapPoint.from_coords(self.point.x + 1, self.point.y)
        elif direction == DirectionsEnum.DOWN:
            mp = MapPoint.from_coords(self.point.x + 1, self.point.y - 1)
        elif direction == DirectionsEnum.DOWN_LEFT:
            mp = MapPoint.from_coords(self.point.x, self.point.y - 1)
        elif direction == DirectionsEnum.LEFT:
            mp = MapPoint.from_coords(self.point.x - 1, self.point.y - 1)
        elif direction == DirectionsEnum.UP_LEFT:
            mp = MapPoint.from_coords(self.point.x - 1, self.point.y)
        elif direction == DirectionsEnum.UP:
            mp = MapPoint.from_coords(self.point.x - 1, self.point.y + 1)
        elif direction == DirectionsEnum.UP_RIGHT:
            mp = MapPoint.from_coords(self.point.x, self.point.y + 1)
        else:
            raise ValueError(f"invalid orientation : {direction}")
        if MapPoint.is_in_map(mp.point.x, mp.point.y):
            return mp
        return None

    @staticmethod
    def from_cell_id(cell_id: int) -> "MapPoint":
        point = CELL_POINT_BY_ID[cell_id]
        map_point = MapPoint(cell_id, point)
        return map_point

    @staticmethod
    def from_coords(x: int, y: int) -> "MapPoint":
        cell_id = (x - y) * MAP_WIDTH + y + (x - y) // 2
        map_point = MapPoint(cell_id, Point(x, y))
        return map_point

    @staticmethod
    def is_in_map(x: int, y: int) -> bool:
        return 0 <= x + y < MAP_WIDTH * 2 and 0 <= x - y < MAP_HEIGHT * 2

    def allows_map_change_to_direction(self, map_id: int, direction: DirectionsEnum):

        map_change_data = (
            MapReader().get_cell_data_by_cell_id(map_id, self.cell_id).mapChangeData
        )

        if direction == DirectionsEnum.RIGHT:
            return (
                bool(map_change_data & 1)
                or (
                    (self.cell_id + 1) % (MAP_WIDTH * 2) == 0
                    and bool(map_change_data & 2)
                )
                or (
                    (self.cell_id + 1) % (MAP_WIDTH * 2) == 0
                    and bool(map_change_data & 128)
                )
            )
        elif direction == DirectionsEnum.LEFT:
            return (
                (self.point.x == -self.point.y and bool(map_change_data & 8))
                or bool(map_change_data & 16)
                or (self.point.x == -self.point.y and bool(map_change_data & 32))
            )
        elif direction == DirectionsEnum.UP:
            return (
                (self.cell_id < MAP_WIDTH and bool(map_change_data & 32))
                or bool(map_change_data & 64)
                or (self.cell_id < MAP_WIDTH and bool(map_change_data & 128))
            )
        elif direction == DirectionsEnum.DOWN:
            return (
                (
                    self.cell_id >= MAP_COUNT_CELL - MAP_WIDTH
                    and bool(map_change_data & 2)
                )
                or bool(map_change_data & 4)
                or (
                    self.cell_id >= MAP_COUNT_CELL - MAP_WIDTH
                    and bool(map_change_data & 8)
                )
            )

        return False
