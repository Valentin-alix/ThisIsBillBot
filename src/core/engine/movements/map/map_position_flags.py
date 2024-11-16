from D3Database.data_center.data_reader import DataReader


def allow_monster_agression(m_flags: int) -> bool:
    return (m_flags & 1048576) != 0


def allow_teleport_from(m_flags: int) -> bool:
    return (m_flags & 8) != 0


def allow_teleport_to(m_flags: int) -> bool:
    return (m_flags & 4) != 0


def allow_teleport_everywhere(m_flags: int) -> bool:
    return (m_flags & 2048) != 0


if __name__ == "__main__":
    map_data = DataReader().map_pos_by_map_id[191105026]
    print(allow_teleport_to(map_data.m_flags))
