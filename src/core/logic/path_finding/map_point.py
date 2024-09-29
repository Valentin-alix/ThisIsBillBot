from dataclasses import dataclass
from src.core.logic.path_finding.consts import MAP_HEIGHT, MAP_WIDTH
from src.core.logic.path_finding.map_tools import MapTools
from src.core.logic.path_finding.point import Point


def get_cells_pos():
    cells_pos: dict[int, Point] = {}
    i_width: int = 0
    start_x: int = 0
    start_y: int = 0
    cell: int = 0

    for _ in range(MAP_HEIGHT):
        for i_width in range(MAP_WIDTH):
            cells_pos[cell] = Point(start_x + i_width, start_y + i_width)
            cell += 1

        start_x += 1

        for i_width in range(MAP_WIDTH):
            cells_pos[cell] = Point(start_x + i_width, start_y + i_width)
            cell += 1

        start_y -= 1

    return cells_pos


CELLS_POS: dict[int, Point] = get_cells_pos()


@dataclass
class MapPoint:
    cell_id: int
    point: Point

    @staticmethod
    def from_cell_id(cell_id: int) -> "MapPoint":
        point = CELLS_POS[cell_id]
        map_point = MapPoint(cell_id, point)
        return map_point

    @staticmethod
    def from_coords(x: int, y: int) -> "MapPoint":
        cell_id = MapTools.get_cell_id_by_coord(x, y)
        map_point = MapPoint(cell_id, Point(x, y))
        return map_point

    @staticmethod
    def is_in_map(x: int, y: int) -> bool:
        return (
            x + y >= 0
            and x - y >= 0
            and x - y < MAP_HEIGHT * 2
            and x + y < MAP_WIDTH * 2
        )
