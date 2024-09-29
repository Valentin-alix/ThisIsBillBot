from src.core.logic.path_finding.point import Point


VECTOR_RIGHT: Point = Point(1, 1)
VECTOR_DOWN_RIGHT: Point = Point(1, 0)
VECTOR_DOWN: Point = Point(1, -1)
VECTOR_DOWN_LEFT: Point = Point(0, -1)
VECTOR_LEFT: Point = Point(-1, -1)
VECTOR_UP_LEFT: Point = Point(-1, 0)
VECTOR_UP: Point = Point(-1, 1)
VECTOR_UP_RIGHT: Point = Point(0, 1)

MAP_WIDTH: int = 14
MAP_HEIGHT: int = 20
MAP_COUNT_CELL = MAP_WIDTH * MAP_HEIGHT * 2

MIN_X_COORD: int = 0
MAX_X_COORD: int = 33
MIN_Y_COORD: int = -19
MAX_Y_COORD: int = 13

MAX_PATH_LENGTH: int = 100
HV_COST: int = 10
DIAG_COST: int = 15
HEURISTIC_COST: int = 10
INFINITE_COST: int = 99999999
