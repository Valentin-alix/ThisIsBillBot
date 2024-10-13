from src.core.data_center.map_reader import MapReader


def get_linked_zone_rp(map_id: int, cell_id: int) -> int:
    cell_data = MapReader().get_cell_data_by_cell_id(map_id, cell_id)
    return (cell_data.linkedZone & 240) >> 4
