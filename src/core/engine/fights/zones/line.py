from dataclasses import dataclass

from dofus_unity_reader.enums.directions import DirectionsEnum
from dofus_unity_reader.grid.map_point import MAP_POINT_BY_COORD, MapPoint
from python_utils.cache import cache

from src.core.engine.fights.zones.zone import Zone


@dataclass(frozen=True)
class Line(Zone):
    alternative_size: int
    size: int
    caster_mp: MapPoint | None = None
    stop_at_target: bool = False

    @property
    def min_radius(self):
        return self.alternative_size

    @property
    def radius(self):
        return self.size

    @cache
    def get_mps(self, mp: MapPoint, direction: DirectionsEnum) -> set[MapPoint]:
        mps: set[MapPoint] = set()
        coords: list[tuple[int, int]] = []

        origin_mp = mp if not self.caster_mp else self.caster_mp
        length: int = (
            self.radius if not self.caster_mp else self.radius + self.min_radius - 1
        )
        if self.caster_mp and self.stop_at_target:
            distance = origin_mp.distance_to_map_point(mp)
            length = int(min((distance, length)))

        for radius in range(self.min_radius, length + 1):
            match direction:
                case DirectionsEnum.LEFT:
                    coords.append((origin_mp.x - radius, origin_mp.y - radius))
                case DirectionsEnum.UP:
                    coords.append((origin_mp.x - radius, origin_mp.y + radius))
                case DirectionsEnum.RIGHT:
                    coords.append((origin_mp.x + radius, origin_mp.y + radius))
                case DirectionsEnum.DOWN:
                    coords.append((origin_mp.x + radius, origin_mp.y - radius))
                case DirectionsEnum.UP_LEFT:
                    coords.append((origin_mp.x - radius, origin_mp.y))
                case DirectionsEnum.DOWN_LEFT:
                    coords.append((origin_mp.x, origin_mp.y - radius))
                case DirectionsEnum.DOWN_RIGHT:
                    coords.append((origin_mp.x + radius, origin_mp.y))
                case DirectionsEnum.UP_RIGHT:
                    coords.append((origin_mp.x, origin_mp.y + radius))
        for coord in coords:
            if coord in MAP_POINT_BY_COORD:
                mps.add(MapPoint.from_coords(*coord))

        return mps
