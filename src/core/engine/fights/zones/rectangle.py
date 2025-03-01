from dataclasses import dataclass
from math import floor

from dofus_unity_reader.game_constants.directions import DirectionsEnum
from dofus_unity_reader.grid.map_point import MAP_POINT_BY_COORD, MapPoint
from python_utils.cache import cache

from src.core.engine.fights.zones.zone import Zone


@dataclass(frozen=True)
class Rectangle(Zone):
    alternative_size: int
    size: int

    @property
    def width(self):
        return 1 + self.size * 2

    @property
    def height(self):
        return 1 + self.alternative_size

    @cache
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
