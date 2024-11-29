from dataclasses import dataclass

from dofus_unity_reader.grid.map_point import MapPoint


@dataclass
class NodeMapPoint:
    mp: MapPoint
    cost_to_node: float = float("inf")
    cost_to_end: float = float("inf")
    total_cost: float = float("inf")
    parent: "NodeMapPoint|None" = None
    in_open_set: bool = False
    is_closed: bool = False

    def __eq__(self, other: object) -> bool:
        return isinstance(other, NodeMapPoint) and self.mp.cell_id == other.mp.cell_id

    def __hash__(self) -> int:
        return self.mp.cell_id.__hash__()

    def __lt__(self, other: "NodeMapPoint") -> bool:
        if self.total_cost == other.total_cost:
            return self.mp.cell_id < other.mp.cell_id
        return self.total_cost < other.total_cost
