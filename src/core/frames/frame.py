from collections.abc import Callable
from dataclasses import dataclass, field
from threading import Event, Timer

from google.protobuf.message import Message

from src.core.events_manager.event_manager import EventManager
from src.core.events_manager.priority import PriorityEnum
from src.core.signals.player_signals import GameInfoSignals, InventorySignals
from src.core.states.game_state import GameState
from src.services.human_timings import get_random_range
from src.services.logging_utils.contextual_logger import ContextualLogger


@dataclass
class Frame(ContextualLogger):
    event_manager: EventManager
    game_state: GameState
    game_info_signals: GameInfoSignals
    inventory_signals: InventorySignals
    is_playing_event: Event

    priority: PriorityEnum = field(default=PriorityEnum.FRAME, init=False)

    _timers: list[Timer] = field(init=False, default_factory=list[Timer])

    def __post_init__(self) -> None:
        self.game_info_signals.disconnected.connect(self.on_disconnected)

    def on_disconnected(self) -> None:
        self.cancel_timers()
        for field_name in dir(self):
            if field_name.startswith("__"):
                continue
            field_value = getattr(self, field_name)
            if hasattr(field_value, "clear_state"):
                field_value.clear_state()

    def run_timer(self, range_time: tuple[float, float] | float, func: Callable[[], None]) -> None:
        if isinstance(range_time, tuple):
            wait_time = get_random_range(range_time)
        else:
            wait_time = range_time
        timer = Timer(wait_time, lambda: self.run_timed_func(timer, func))
        with self.event_manager.lock:
            self._timers.append(timer)
        timer.start()

    def run_timed_func(self, timer: Timer, func: Callable[[], None]) -> None:
        with self.event_manager.lock:
            if timer not in self._timers:
                return
            self._timers.remove(timer)
            func()

    def cancel_timers(self) -> None:
        with self.event_manager.lock:
            for timer in self._timers:
                timer.cancel()
            self._timers.clear()

    def unregister_listener(self, event_type: type[Message], reason: str = "") -> None:
        """Remove a listener during execution; behavior completion already clears all listeners."""
        if reason:
            self.logger.debug(f"Manual listener cleanup: {event_type.__name__} - {reason}")
        self.event_manager.clear_listener_by_origin_and_type(event_type, self)
