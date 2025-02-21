from dataclasses import dataclass

from src.services.logging_utils.contextual_logger import ContextualLogger


@dataclass
class State(ContextualLogger): ...
