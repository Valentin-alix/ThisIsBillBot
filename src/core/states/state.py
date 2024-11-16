from abc import ABC
from dataclasses import dataclass

from src.services.logging.logger import Logger


@dataclass
class State(ABC):
    logger: Logger
