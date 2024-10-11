from dataclasses import dataclass

from src.core.logic.grid.directions import DirectionsEnum
from src.core.logic.grid.map_point import MapPoint, MAP_POINT_BY_COORD
from src.core.logic.zones.zone import Zone


@dataclass
class Fork(Zone):
    size: int

    def __post_init__(self):
        self.length = self.size + 1

    def get_mps(self, mp: MapPoint, direction: DirectionsEnum) -> set[MapPoint]:
        mps: set[MapPoint] = set()
        sign: int = (
            -1 if direction in [DirectionsEnum.UP_LEFT, DirectionsEnum.DOWN_LEFT] else 1
        )
        axis_flag: bool = direction in [
            DirectionsEnum.UP_LEFT,
            DirectionsEnum.DOWN_RIGHT,
        ]
        coords: list[tuple[int, int]] = []
        for i in range(1, self.length + 1):
            for j in range(-1, 1 + 1):
                if axis_flag:
                    coords.append((mp.x + i * sign, mp.y + j * i))
                else:
                    coords.append((mp.x + j * i, mp.y + i * sign))

        for coord in coords:
            if coord in MAP_POINT_BY_COORD:
                mps.add(MapPoint.from_coords(*coord))

        return mps
