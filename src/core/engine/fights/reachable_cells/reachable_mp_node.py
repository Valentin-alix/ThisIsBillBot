from dataclasses import dataclass

from D3Database.grid.map_point import MapPoint


@dataclass
class ReachableMpNode:
    mp: MapPoint
    best_remaining_pm_no_tackle: int

    def __hash__(self):
        return self.mp.__hash__()
