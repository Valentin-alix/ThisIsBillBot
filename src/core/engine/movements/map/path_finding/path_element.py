from dataclasses import dataclass

from d3_database.enums.directions import DirectionsEnum
from d3_database.grid.map_point import MapPoint


@dataclass
class PathElement:
    step: MapPoint
    orientation: DirectionsEnum
