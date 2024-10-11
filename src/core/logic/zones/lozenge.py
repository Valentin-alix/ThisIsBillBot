from dataclasses import dataclass

from src.core.logic.grid.directions import DirectionsEnum
from src.core.logic.grid.map_point import MapPoint, MAP_POINT_BY_COORD
from src.core.logic.zones.zone import Zone


@dataclass
class Lozenge(Zone):
    alternative_size: int
    size: int

    def __post_init__(self):
        self.min_radius = self.alternative_size
        self.radius = self.size

    def get_mps(self, mp: MapPoint, direction: DirectionsEnum | None) -> set[MapPoint]:
        mps: set[MapPoint] = set()
        if self.radius == 0:
            if self.min_radius == 0:
                mps.add(mp)
            return mps

        for radius in range(self.radius, self.min_radius - 1, -1):
            for i in range(-radius, radius + 1):
                j = radius - abs(i)
                for dy in (-j, j):
                    coord = mp.x + i, mp.y + dy
                    if coord in MAP_POINT_BY_COORD:
                        mps.add(MapPoint.from_coords(*coord))

        return mps
