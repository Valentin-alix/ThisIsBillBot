from abc import ABC, abstractmethod

from grid.directions import DirectionsEnum
from grid.map_point import MapPoint


class Zone(ABC):
    @abstractmethod
    def get_mps(self, mp: MapPoint, direction: DirectionsEnum) -> set[MapPoint]: ...
