from enum import IntEnum

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
