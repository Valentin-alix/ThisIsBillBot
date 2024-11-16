from dataclasses import dataclass

from D3Database.enums.directions import DirectionsEnum
from D3Database.grid.map_point import MapPoint


@dataclass
class PathElement:
    step: MapPoint
    orientation: DirectionsEnum
