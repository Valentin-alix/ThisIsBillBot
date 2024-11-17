from abc import ABC
from dataclasses import dataclass

from src.services.logging.contextual_logger import ContextualLogger


@dataclass
class State(ABC, ContextualLogger): ...
