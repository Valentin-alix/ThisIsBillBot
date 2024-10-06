from dataclasses import dataclass
from typing import Any

from src.core.logic.grid.map_point import MapPoint


@dataclass
class NodeMapPoint:
    mp: MapPoint
    cost_to_node: float = float("inf")
    cost_to_end: float = float("inf")
    total_cost: float = float("inf")
    parent: "NodeMapPoint|None" = None
    in_open_set: bool = False
    is_closed: bool = False

    def __hash__(self) -> int:
        return self.mp.cell_id.__hash__()

    def __eq__(self, other: Any) -> bool:
        if type(other) is not NodeMapPoint:
            return False
        return self.mp.cell_id == other.mp.cell_id

    def __lt__(self, other: "NodeMapPoint") -> bool:
        return self.total_cost < other.total_cost
