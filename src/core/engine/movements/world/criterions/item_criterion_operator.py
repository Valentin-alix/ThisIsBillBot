from dataclasses import dataclass
from typing import ClassVar


@dataclass
class ItemCriterionOperator:
    SUPERIOR: ClassVar[str] = ">"
    INFERIOR: ClassVar[str] = "<"
    EQUAL: ClassVar[str] = "="
    DIFFERENT: ClassVar[str] = "!"
    OPERATORS_LIST: ClassVar[list[str]] = [
        SUPERIOR,
        INFERIOR,
        EQUAL,
        DIFFERENT,
        "#",
        "~",
        "s",
        "S",
        "e",
        "E",
        "v",
        "i",
        "X",
        "/",
    ]

    operator: str

    @property
    def text(self) -> str:
        return self.operator

    def compare(self, left_member_value: float, right_member_value: float) -> bool:
        if self.operator == self.SUPERIOR:
            if left_member_value > right_member_value:
                return True
        elif self.operator == self.INFERIOR:
            if left_member_value < right_member_value:
                return True
        elif self.operator == self.EQUAL:
            if left_member_value == right_member_value:
                return True
        elif self.operator == self.DIFFERENT:
            if left_member_value != right_member_value:
                return True
        return False
