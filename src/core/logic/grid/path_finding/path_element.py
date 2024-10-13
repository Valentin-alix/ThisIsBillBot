from dataclasses import dataclass

from grid.directions import DirectionsEnum
from grid.map_point import MapPoint


@dataclass
class PathElement:
    step: MapPoint
    orientation: DirectionsEnum
