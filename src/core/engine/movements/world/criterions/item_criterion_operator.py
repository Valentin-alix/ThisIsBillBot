from dataclasses import dataclass
from typing import ClassVar


@dataclass
class ItemCriterionOperator:
    SUPERIOR: ClassVar[str] = ">"
    INFERIOR: ClassVar[str] = "<"
    EQUAL: ClassVar[str] = "="
    DIFFERENT: ClassVar[str] = "!"
    EQUIPPED: ClassVar[str] = "E"
    NOT_EQUIPPED: ClassVar[str] = "X"
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

    @property
    def html_text(self) -> str:
        if self.operator == self.SUPERIOR:
            return "&gt"
        if self.operator == self.INFERIOR:
            return "&lt"
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
