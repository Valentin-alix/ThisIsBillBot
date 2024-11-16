from dataclasses import dataclass

from D3Database.enums.directions import DirectionsEnum
from D3Database.grid.map_point import MAP_POINT_BY_COORD, MapPoint
from D3Database.utils import cache
from src.core.engine.fights.zones.zone import Zone


@dataclass(frozen=True)
class Lozenge(Zone):
    alternative_size: int
    size: int

    @property
    def min_radius(self):
        return self.alternative_size

    @property
    def radius(self):
        return self.size

    @cache
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
