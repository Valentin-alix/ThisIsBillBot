from src.interfaces.enums.DirectionsEnum import DirectionsEnum


def get_cell_id_by_key(key: int):
    return key & 0x3FF


def get_direction_by_key(key: int):
    return DirectionsEnum((key >> 12) & 7)
