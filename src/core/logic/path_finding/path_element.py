from dataclasses import dataclass
from src.core.logic.path_finding.map_point import MapPoint


@dataclass
class PathElement:
    step: MapPoint
    orientation: int
