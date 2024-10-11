from abc import ABC, abstractmethod

from src.core.logic.grid.directions import DirectionsEnum
from src.core.logic.grid.map_point import MapPoint


class Zone(ABC):
    @abstractmethod
    def get_mps(self, mp: MapPoint, direction: DirectionsEnum) -> set[MapPoint]: ...
