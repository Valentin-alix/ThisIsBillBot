from dataclasses import dataclass

from models.world_graph import Vertice
from src.core.data_center.data_reader import DataReader
from src.core.logic.flags.map_position_flags import allow_teleport_to
from src.core.logic.world.astar_vertice import AstarWorld


@dataclass
class AstarAllowHavreSac(AstarWorld):
    def is_goal_reached(self, current: Vertice, ends: set[Vertice]) -> bool:
        curr_map_pos = DataReader().map_pos_by_map_id[current.m_mapId]
        return allow_teleport_to(curr_map_pos.m_flags)
