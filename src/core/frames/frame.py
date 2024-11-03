from dataclasses import dataclass, field
from threading import Event, Timer
from typing import Callable

from src.common.logger import Logger
from src.common.timing import get_random_range
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

    _timers: list[Timer] = field(default_factory=list, init=False)

    def run_timer(
        self, range_time: tuple[float, float] | float, func: Callable[[], None]
    ) -> None:
        if isinstance(range_time, tuple):
            wait_time = get_random_range(range_time)
        else:
            wait_time = range_time
        self.logger.info(f"Waiting for {wait_time} before executing function {func}")
        timer = Timer(wait_time, lambda: self.run_timed_func(func))
        self._timers.append(timer)
        timer.start()

    def run_timed_func(self, func: Callable[[], None]):
        with self.event_manager.lock:
            func()
