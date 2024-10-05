from dataclasses import dataclass, field
from typing import Callable

from google.protobuf.message import Message

from src.interfaces.enums.priority import PriorityEnum


@dataclass
class Listener:
    callback: Callable[[Message], None]
    originator: object
    once: bool = field(default=False)
    priority: int = field(default=PriorityEnum.NORMAL)

    def __lt__(self, other: "Listener") -> bool:
        return self.priority < other.priority
