from abc import ABC, abstractmethod

from d3_database.enums.directions import DirectionsEnum
from d3_database.grid.map_point import MapPoint


class Zone(ABC):
    @abstractmethod
    def get_mps(self, mp: MapPoint, direction: DirectionsEnum) -> set[MapPoint]: ...
