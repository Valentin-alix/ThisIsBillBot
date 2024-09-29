from dataclasses import dataclass

from src.core.logic.path_finding.map_point import MapPoint
from src.core.logic.path_finding.path_element import PathElement


@dataclass
class MovementPath:
    start: MapPoint
    end: MapPoint
    path: list[PathElement]
