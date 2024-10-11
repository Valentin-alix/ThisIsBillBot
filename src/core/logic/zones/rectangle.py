from dataclasses import dataclass
from math import floor

from src.core.logic.grid.directions import DirectionsEnum
from src.core.logic.grid.map_point import MapPoint, MAP_POINT_BY_COORD
from src.core.logic.zones.zone import Zone


@dataclass
class Rectangle(Zone):
    alternative_size: int
    size: int

    def __post_init__(self):
        self.width = 1 + self.size * 2
        self.height = 1 + self.alternative_size

    def get_mps(self, mp: MapPoint, direction: DirectionsEnum) -> set[MapPoint]:
        mps: set[MapPoint] = set()
        coords: list[tuple[int, int]] = []
        sign: int = (
            -1 if direction in [DirectionsEnum.UP_LEFT, DirectionsEnum.DOWN_LEFT] else 1
        )
        axis_flag: bool = direction in [
            DirectionsEnum.UP_LEFT,
            DirectionsEnum.DOWN_LEFT,
        ]
        for i in range(self.height):
            for j in range(self.width):
                if axis_flag:
                    x, y = mp.x + j - floor(self.width / 2), mp.y + i * sign
                else:
                    x, y = mp.x + i * sign, mp.y + j - floor(self.width / 2)
                coords.append((x, y))

        for coord in coords:
            if coord in MAP_POINT_BY_COORD:
                mps.add(MapPoint.from_coords(*coord))

        return mps
