from abc import ABC
from dataclasses import dataclass, field

from src.event_manager import EventManager
from src.interfaces.enums.priority import PriorityEnum


@dataclass
class Frame(ABC):
    event_manager: EventManager

    priority: PriorityEnum = field(default=PriorityEnum.MAX, init=False)
