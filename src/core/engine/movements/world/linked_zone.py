from DBDofusUnity.dofus_unity_reader.data_center.map_reader import MapReader
from DBDofusUnity.dofus_unity_reader.game_constants.map_id import LINKED_ZONE_MASK, LINKED_ZONE_SHIFT


def get_linked_zone_rp(map_id: int, cell_id: int) -> int:
    cell_data = MapReader().get_cell_data_by_cell_id(map_id, cell_id)
    return (cell_data.linkedZone & LINKED_ZONE_MASK) >> LINKED_ZONE_SHIFT
