from abc import ABC
from dataclasses import dataclass

from src.common.logger import Logger


@dataclass
class State(ABC):
    logger: Logger
