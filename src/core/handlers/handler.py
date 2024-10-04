from abc import ABC
from dataclasses import dataclass

from src.signals.message_events import MessageEvents


@dataclass
class Handler(ABC):
    msg_event: MessageEvents
