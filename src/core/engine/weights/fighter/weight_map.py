from dofus_unity_reader.data_center.data_reader import DataReader

from src.core.engine.movements.map.map_position_flags import (
    allow_monster_agression,
)


def get_additional_weight_by_map_id(map_id: int, player_level: int):
    map_pos_data = DataReader().map_info_by_map_id[map_id]
    m_flags = map_pos_data.m_flags
    if not allow_monster_agression(m_flags):
        weight = 0
    else:
        sub_area_lvl = DataReader().sub_area_by_id[map_pos_data.subAreaId].level
        weight = 1000 / (1 + abs(sub_area_lvl - player_level))
    return weight
