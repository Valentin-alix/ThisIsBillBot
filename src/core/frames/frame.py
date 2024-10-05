from abc import ABC
from dataclasses import dataclass

from src.event_manager import EventManager


@dataclass
class Frame(ABC):
    event_manager: EventManager
