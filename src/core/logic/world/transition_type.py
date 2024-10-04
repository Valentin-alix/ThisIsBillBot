from enum import IntEnum


class TransitionTypeEnum(IntEnum):
    UNSPECIFIED = 0
    SCROLL = 1
    SCROLL_ACTION = 2
    MAP_EVENT = 4
    MAP_ACTION = 8
    MAP_OBSTACLE = 16
    INTERACTIVE = 32
    NPC_ACTION = 64
    ITEM_TELEPORT = 128
    ZAAP = 256
