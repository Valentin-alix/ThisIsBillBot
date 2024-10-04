from dataclasses import dataclass

from src.core.logic.grid.map_point import MapPoint


@dataclass
class PathElement:
    step: MapPoint
    orientation: int
