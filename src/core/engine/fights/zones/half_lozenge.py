from dataclasses import dataclass

from dofus_unity_reader.enums.directions import DirectionsEnum
from dofus_unity_reader.grid.map_point import MAP_POINT_BY_COORD, MapPoint
from python_utils.cache import cache

from src.core.engine.fights.zones.zone import Zone


@dataclass(frozen=True)
class HalfLozenge(Zone):
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

        if self.min_radius == 0:
            mps.add(mp)

        coords: list[tuple[int, int]] = []
        for i in range(1, self.radius + 1):
            match direction:
                case DirectionsEnum.UP_LEFT:
                    coords.append((mp.x + i, mp.y + i))
                    coords.append((mp.x + i, mp.y - i))
                case DirectionsEnum.UP_RIGHT:
                    coords.append((mp.x - i, mp.y - i))
                    coords.append((mp.x + i, mp.y - i))
                case DirectionsEnum.DOWN_RIGHT:
                    coords.append((mp.x - i, mp.y + i))
                    coords.append((mp.x - i, mp.y - i))
                case DirectionsEnum.DOWN_LEFT:
                    coords.append((mp.x - i, mp.y + i))
                    coords.append((mp.x + i, mp.y + i))

        for coord in coords:
            if coord in MAP_POINT_BY_COORD:
                mps.add(MapPoint.from_coords(*coord))

        return mps
