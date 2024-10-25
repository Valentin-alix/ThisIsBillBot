from dataclasses import dataclass

from d3_mapping.models.p_enum import PEnum
from d3_mapping.models.p_message import PMessage


@dataclass(frozen=True)
class PFile:
    filename: str
    package: str | None
    imports: list[str]
    messages: list[PMessage]
    enums: list[PEnum]

    def __hash__(self):
        return self.filename.__hash__()
