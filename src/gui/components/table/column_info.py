from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable

from PyQt5.QtWidgets import QWidget


class SearchType(Enum):
    CONTAINS = auto()
    EXACT = auto()


@dataclass
class ColumnInfo:
    name: str
    is_hidden: bool = False
    search_type: SearchType | None = field(default=SearchType.CONTAINS)
    get_texts_func: Callable[[QWidget], list[str]] | None = field(default=None)
