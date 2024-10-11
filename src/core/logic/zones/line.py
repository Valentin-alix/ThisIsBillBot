from dataclasses import dataclass

from src.core.logic.grid.directions import DirectionsEnum
from src.core.logic.grid.map_point import MapPoint, MAP_POINT_BY_COORD
from src.core.logic.zones.zone import Zone


@dataclass
class Line(Zone):
    alternative_size: int
    size: int
    caster_mp: MapPoint | None = None
    stop_at_target: bool = False

    def __post_init__(self):
        self.min_radius = self.alternative_size
        self.radius = self.size

    def get_mps(self, mp: MapPoint, direction: DirectionsEnum) -> set[MapPoint]:
        mps: set[MapPoint] = set()
        coords: list[tuple[int, int]] = []

        origin_mp = mp if not self.caster_mp else self.caster_mp
        length: int = (
            self.radius if not self.caster_mp else self.radius + self.min_radius - 1
        )
        if self.caster_mp and self.stop_at_target:
            distance = origin_mp.distance_to_map_point(mp)
            length = min((distance, length))

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
