from abc import ABC
from dataclasses import dataclass, field

from src.common.logger import Logger
from src.core.states.game_state import GameState
from src.event_manager import EventManager
from src.interfaces.enums.priority import PriorityEnum


@dataclass
class Frame(ABC):
    event_manager: EventManager
    game_state: GameState
    logger: Logger

    priority: PriorityEnum = field(default=PriorityEnum.FRAME, init=False)
