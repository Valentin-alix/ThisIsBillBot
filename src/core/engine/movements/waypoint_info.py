from dataclasses import dataclass

from D3Database.models.datas.map_positions_root import MapPositionsRootItem


@dataclass
class WaypointInfoNode:
    map_id: int
    map_position: MapPositionsRootItem
    dist_to_target: float
