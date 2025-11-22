from enum import StrEnum, auto


class RejectionStat(StrEnum):
    MAX_CAST_PER_TARGET = auto()
    MAX_CAST_PER_TURN = auto()
    INSUFICIENT_AP = auto()
    INITIAL_COOLDOWN = auto()
    GLOBAL_COOLDOWN = auto()
    MIN_CAST_INTERVAL = auto()
    CELL_NOT_WALKABLE = auto()
    NO_LOS = auto()
