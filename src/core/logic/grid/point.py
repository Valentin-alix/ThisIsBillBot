from dataclasses import dataclass
from functools import cached_property

from src.core.logic.grid.consts import MAP_HEIGHT, MAP_WIDTH


def get_cell_point_by_id() -> dict[int, "Point"]:
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


@dataclass(frozen=True)
class Point:
    x: int
    y: int

    def distance_to_point(self, point: "Point") -> float:
        return abs(self.x - point.x) + abs(self.y - point.y)

    def is_diagonal_move(self, point: "Point") -> bool:
        return not (self.y == point.y or self.x == point.x)

    @cached_property
    def get_side_points(self) -> list["Point"]:
        """get the four point next to this point (not in diag)"""
        return [
            Point(x=self.x + 1, y=self.y),
            Point(x=self.x, y=self.y + 1),
            Point(x=self.x - 1, y=self.y),
            Point(x=self.x, y=self.y - 1),
        ]

    @staticmethod
    def from_cell_id(cell_id: int) -> "Point":
        return CELL_POINT_BY_CELL_ID[cell_id]

    def is_in_map(self) -> bool:
        return (
            0 <= self.x + self.y < MAP_WIDTH * 2
            and 0 <= self.x - self.y < MAP_HEIGHT * 2
        )


CELL_POINT_BY_CELL_ID: dict[int, Point] = get_cell_point_by_id()

VECTOR_RIGHT: Point = Point(1, 1)
VECTOR_DOWN_RIGHT: Point = Point(1, 0)
VECTOR_DOWN: Point = Point(1, -1)
VECTOR_DOWN_LEFT: Point = Point(0, -1)
VECTOR_LEFT: Point = Point(-1, -1)
VECTOR_UP_LEFT: Point = Point(-1, 0)
VECTOR_UP: Point = Point(-1, 1)
VECTOR_UP_RIGHT: Point = Point(0, 1)
