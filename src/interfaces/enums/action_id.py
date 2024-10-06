from enum import IntEnum


class ActionId(IntEnum):
    TURN = 2
    PLAYER_END_TURN = 4
    PLAYER_MOVED = 8
    PLAYER_ACTION_PLAYED = 11
