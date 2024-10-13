from enum import Enum, IntEnum, auto


class TypeEffect(Enum):
    SHIELD_PERCENT_LEVEL = auto()
    MALUS_LIFE_PERCENT = auto()


class EffectElement(IntEnum):
    STRENGTH = 1
    INTELLIGENCE = 2
    CHANCE = 3
    AGILITY = 4
