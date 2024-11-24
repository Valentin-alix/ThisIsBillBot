from dataclasses import dataclass

from d3_database.enums.directions import DirectionsEnum
from d3_database.grid.map_point import MAP_POINT_BY_COORD, MapPoint
from d3_database.utils import cache

from src.core.engine.fights.zones.zone import Zone


@dataclass(frozen=True)
class Cone(Zone):
    alternative_size: int
    size: int

    @property
    def min_radius(self):
        return self.alternative_size

    @property
    def radius(self):
        return self.size

    @cache
    def get_mps(self, mp: MapPoint, direction: DirectionsEnum) -> set[MapPoint]:
        mps: set[MapPoint] = set()
        if self.radius == 0:
            if self.min_radius == 0:
                mps.add(mp)
            return mps

        coords: list[tuple[int, int]] = []

        match direction:
            case DirectionsEnum.UP_LEFT:
                for step, i in enumerate(range(mp.x, mp.x - self.radius - 1, -1)):
                    for j in range(-step, step + 1):
                        if not abs(mp.x - i) + abs(j) >= self.min_radius:
                            continue
                        coords.append((i, j + mp.y))
            case DirectionsEnum.DOWN_LEFT:
                for step, j in enumerate(range(mp.y, mp.y - self.radius - 1, -1)):
                    for i in range(-step, step + 1):
                        if not abs(i) + abs(mp.y - j) >= self.min_radius:
                            continue
                        coords.append((i + mp.x, j))
            case DirectionsEnum.DOWN_RIGHT:
                for step, i in enumerate(range(mp.x, mp.x + self.radius + 1)):
                    for j in range(-step, step + 1):
                        if not abs(mp.x - i) + abs(j) >= self.min_radius:
                            continue
                        coords.append((i, j + mp.y))
            case DirectionsEnum.UP_RIGHT:
                for step, j in enumerate(range(mp.y, mp.y + self.radius + 1)):
                    for i in range(-step, step + 1):
                        if not abs(i) + abs(mp.y - j) >= self.min_radius:
                            continue
                        coords.append((i + mp.x, j))

        for coord in coords:
            if coord in MAP_POINT_BY_COORD:
                mps.add(MapPoint.from_coords(*coord))

        return mps
