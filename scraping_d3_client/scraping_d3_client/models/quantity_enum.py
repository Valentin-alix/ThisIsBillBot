from enum import IntEnum


class QuantityEnum(IntEnum):
    VALUE_1 = 1
    VALUE_10 = 10
    VALUE_100 = 100
    VALUE_1000 = 1000

    def __str__(self) -> str:
        return str(self.value)


class QuantityIndex(IntEnum):
    ONE = 0
    TEN = 1
    HUNDRED = 2
    THOUSAND = 3
