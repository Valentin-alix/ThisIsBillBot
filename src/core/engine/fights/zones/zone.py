from abc import ABC, abstractmethod

from DBDofusUnity.dofus_unity_reader.game_constants.directions import DirectionsEnum
from DBDofusUnity.dofus_unity_reader.grid.map_point import MapPoint


class Zone(ABC):
    @abstractmethod
    def get_mps(self, mp: MapPoint, direction: DirectionsEnum) -> set[MapPoint]: ...
