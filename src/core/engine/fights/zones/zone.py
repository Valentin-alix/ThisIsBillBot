from abc import ABC, abstractmethod

from D3Database.enums.directions import DirectionsEnum
from D3Database.grid.map_point import MapPoint


class Zone(ABC):
    @abstractmethod
    def get_mps(self, mp: MapPoint, direction: DirectionsEnum) -> set[MapPoint]: ...
