from dataclasses import dataclass, field
from threading import Event, Timer
from typing import Callable

from src.core.events_manager.event_manager import EventManager
from src.core.events_manager.priority import PriorityEnum
from src.core.signals.player_signals import GameInfoSignals, InventorySignals
from src.core.states.game_state import GameState
from src.services.human_timings import get_random_range
from src.services.logging.logger import Logger


@dataclass
class Frame:
    event_manager: EventManager
    game_state: GameState
    game_info_signals: GameInfoSignals
    inventory_signals: InventorySignals
    logger: Logger
    is_playing_event: Event

    priority: PriorityEnum = field(default=PriorityEnum.FRAME, init=False)

    _timers: list[Timer] = field(default_factory=list, init=False)

    def __post_init__(self):
        self.game_info_signals.disconnected.connect(self.on_disconnected)

    def on_disconnected(self):
        for field_name in dir(self):
            if field_name.startswith("__"):
                continue
            field_value = getattr(self, field_name)
            if hasattr(field_value, "clear_state"):
                field_value.clear_state()

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
