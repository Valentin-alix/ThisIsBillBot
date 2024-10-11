from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from threading import Event, Timer
from typing import Callable

from src.common.logger import Logger
from src.common.timing import get_random_range
from src.core.states.game_state import GameState
from src.event_manager import EventManager


@dataclass
class Behavior(ABC):
    event_manager: EventManager
    game_state: GameState
    logger: Logger
    callback: Callable[[str | None], None] | None = field(init=False, default=None)
    parent: "Behavior|None" = field(init=False, default=None)

    is_running: Event = field(init=False, default_factory=Event)
    children: "list[Behavior]" = field(init=False, default_factory=list)
    timers: list[Timer] = field(init=False, default_factory=list)

    @abstractmethod
    def run(self, *args, **kwargs) -> None: ...

    def start(
        self,
        callback: Callable[[str | None], None] | None,
        parent: "Behavior|None",
        *args,
        **kwargs,
    ) -> None:
        self.logger.info(f"starting : {self.__class__}")
        if parent and not parent.is_running.is_set():
            return self.logger.error(
                f"behavior {self.__class__} parent {parent.__class__} is not running"
            )
        if self.is_running.is_set():
            return self.logger.error(f"behavior {self.__class__} is already running")
        self.parent = parent
        if self.parent:
            self.parent.children.append(self)
        self.is_running.set()
        self.callback = callback
        self.run(*args, **kwargs)

    def run_timer(
        self, range_time: tuple[float, float] | float, func: Callable[[], None]
    ) -> None:
        if isinstance(range_time, float):
            wait_time = range_time
        else:
            wait_time = get_random_range(range_time)
        self.logger.info(f"Waiting for {wait_time} before executing function")
        timer = Timer(wait_time, lambda: self.run_timed_func(func))
        self.timers.append(timer)
        timer.start()

    def run_timed_func(self, func: Callable[[], None]):
        with self.event_manager.lock:
            if self.is_running.is_set():
                return func()
        self.logger.info(
            f"behavior {self.__class__} is not running anymore, don't run timed function"
        )

    def stop(self) -> None:
        if not self.is_running.is_set():
            return self.logger.error(
                f"stopped but behavior {self.__class__} is not running "
            )
        self.is_running.clear()

        for timer in self.timers:
            timer.cancel()
        self.timers.clear()

        self.event_manager.clear_listener_by_origin(self)
        self.event_manager.clear_modifier_by_origin(self)

        if self.parent and self in self.parent.children:
            self.parent.children.remove(self)

        self.logger.info(f"Stopped {self.__class__}")

        while self.children:
            child = self.children.pop()
            child.stop()

    def finish(self, error_code: str | None = None) -> None:
        if error_code is not None:
            self.logger.warning(
                f"Stopping {self.__class__} with error code : {error_code}"
            )
        self.stop()
        if self.callback:
            callback = self.callback
            self.callback = None
            callback(error_code)
