from dataclasses import dataclass, field
from enum import Enum, auto


class SearchType(Enum):
    CONTAINS = auto()
    EXACT = auto()


@dataclass
class ColumnInfo:
    name: str
    search_type: SearchType | None = field(default=SearchType.CONTAINS)
