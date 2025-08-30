from dofus_unity_reader.game_constants.map_capability import (
    MapCapabilityFlag,
    does_allow_capability,
)


def allow_monster_agression(m_flags: int) -> bool:
    return does_allow_capability(m_flags, MapCapabilityFlag.ALLOW_MONSTER_AGRESSION)


def allow_teleport_from(m_flags: int) -> bool:
    return does_allow_capability(m_flags, MapCapabilityFlag.ALLOW_TELEPORT_FROM)


def allow_teleport_to(m_flags: int) -> bool:
    return does_allow_capability(m_flags, MapCapabilityFlag.ALLOW_TELEPORT_TO)


def allow_teleport_everywhere(m_flags: int) -> bool:
    return does_allow_capability(m_flags, MapCapabilityFlag.ALLOW_TELEPORT_EVERYWHERE)
