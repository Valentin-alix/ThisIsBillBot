from dataclasses import dataclass

from dofus_unity_reader.game_constants.directions import DirectionsEnum
from dofus_unity_reader.grid.map_point import MapPoint


@dataclass
class PathElement:
    step: MapPoint
    orientation: DirectionsEnum
