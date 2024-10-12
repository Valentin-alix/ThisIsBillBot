from dataclasses import dataclass, field
from threading import Event

from src.common.logger import Logger
from src.core.states.game_state import GameState
from src.event_manager import EventManager
from src.interfaces.enums.priority import PriorityEnum
from src.signals.player_signals import GameInfoSignals


@dataclass
class Frame:
    event_manager: EventManager
    game_state: GameState
    game_info_signals: GameInfoSignals
    logger: Logger
    is_playing_event: Event

    priority: PriorityEnum = field(default=PriorityEnum.FRAME, init=False)
