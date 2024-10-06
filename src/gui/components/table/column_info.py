from dataclasses import dataclass, field
from enum import Enum, auto


class SearchType(Enum):
    CONTAINS = auto()
    EXACT = auto()


@dataclass
class FilterInfo:
    search_type: SearchType = field(default=SearchType.CONTAINS)


@dataclass
class ColumnInfo:
    name: str
    is_hidden: bool = False
    filter_info: FilterInfo | None = field(default_factory=FilterInfo)
