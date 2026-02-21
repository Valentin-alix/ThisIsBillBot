from enum import IntEnum, IntFlag

from utils.cache import cache


class DirectionsEnum(IntEnum):
    RIGHT = 0
    DOWN_RIGHT = 1
    DOWN = 2
    DOWN_LEFT = 3
    LEFT = 4
    UP_LEFT = 5
    UP = 6
    UP_RIGHT = 7

    @classmethod
    def is_orthogonal(cls, direction: "DirectionsEnum") -> bool:
        return (direction & 1) == 1

    @classmethod
    def is_cardinal(cls, direction: "DirectionsEnum") -> bool:
        return (direction & 1) == 0

    @classmethod
    def get_opposite(cls, direction: "DirectionsEnum") -> "DirectionsEnum":
        return DirectionsEnum(direction ^ 4)

    @classmethod
    @cache
    def get_distance(
        cls,
        current_orientation: "DirectionsEnum",
        target_orientation: "DirectionsEnum",
    ) -> int:
        return min(
            abs(target_orientation - current_orientation),
            abs(8 - target_orientation + current_orientation),
        )


class MapChangeFlag(IntFlag):
    RIGHT = 1 << DirectionsEnum.RIGHT
    DOWN_RIGHT = 1 << DirectionsEnum.DOWN_RIGHT
    DOWN = 1 << DirectionsEnum.DOWN
    DOWN_LEFT = 1 << DirectionsEnum.DOWN_LEFT
    LEFT = 1 << DirectionsEnum.LEFT
    UP_LEFT = 1 << DirectionsEnum.UP_LEFT
    UP = 1 << DirectionsEnum.UP
    UP_RIGHT = 1 << DirectionsEnum.UP_RIGHT
