from dataclasses import dataclass

from DBDofusUnity.dofus_unity_reader.data_center.data_reader import DataReader
from DBDofusUnity.dofus_unity_reader.models.world_graph import Vertice

from src.core.engine.movements.map.map_position_flags import allow_teleport_to
from src.core.engine.movements.world.astar_vertice import AstarWorld


@dataclass
class AstarAllowHavreSac(AstarWorld):
    def is_goal_reached(self, current: Vertice, ends: set[Vertice]) -> bool:
        curr_map_pos = DataReader().map_info_by_map_id[current.m_mapId]
        return allow_teleport_to(curr_map_pos.m_flags)
