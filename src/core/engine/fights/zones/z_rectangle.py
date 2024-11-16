from dataclasses import dataclass

from D3Database.enums.directions import DirectionsEnum
from D3Database.grid.map_point import MAP_POINT_BY_COORD, MapPoint
from D3Database.utils import cache
from src.core.engine.fights.zones.zone import Zone


@dataclass(frozen=True)
class ZRectangle(Zone):
    min_radius: int
    alternative_size: int
    size: int
    is_diagonal_free: bool

    @property
    def width(self):
        return self.alternative_size

    @property
    def height(self):
        return self.size if self.size != 0 else self.width

    @cache
    def get_mps(self, mp: MapPoint, direction: DirectionsEnum) -> set[MapPoint]:
        mps: set[MapPoint] = set()

        coords: list[tuple[int, int]] = []

        if self.width == 0 or self.height == 0:
            if self.min_radius == 0 and not self.is_diagonal_free:
                mps.add(mp)
            return mps

        for i in range(mp.x - self.width, mp.x + self.width + 1):
            for j in range(mp.y - self.height, mp.y + self.height + 1):
                if not abs(mp.x - i) + abs(mp.y - j) >= self.min_radius:
                    continue
                if self.is_diagonal_free and abs(mp.x - i) == abs(mp.y - j):
                    continue
                coords.append((i, j))

        for coord in coords:
            if coord in MAP_POINT_BY_COORD:
                mps.add(MapPoint.from_coords(*coord))

        return mps
