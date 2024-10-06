from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from threading import Event, Timer
from typing import Callable

from src.common.logger import Logger
from src.common.timing import get_random_range
from src.event_manager import EventManager


@dataclass
class Behavior(ABC):
    event_manager: EventManager
    callback: Callable[[str | None], None] | None = field(init=False, default=None)
    parent: "Behavior|None" = field(init=False, default=None)

    _is_running: Event = field(init=False, default_factory=Event)
    _children: "list[Behavior]" = field(init=False, default_factory=list)
    _timers: list[Timer] = field(init=False, default_factory=list)

    @abstractmethod
    def run(self, *args, **kwargs) -> None: ...

    def start(
        self,
        callback: Callable[[str | None], None] | None,
        parent: "Behavior|None",
        *args,
        **kwargs,
    ) -> None:
        Logger().info(f"starting : {self.__class__}")
        if parent and not parent._is_running.is_set():
            raise ValueError(
                f"starting behavior {self.__class__} but parent {parent.__class__} is not running"
            )
        if self._is_running.is_set():
            raise ValueError(
                f"starting behavior {self.__class__} but it is already running"
            )
        self.parent = parent
        if self.parent:
            self.parent._children.append(self)
        self._is_running.set()
        self.callback = callback
        self.run(*args, **kwargs)

    def run_timer(self, range_time: tuple[float, float], func: Callable) -> None:
        wait_time = get_random_range(range_time)
        Logger().info(f"Waiting for {wait_time} before executing function")
        timer = Timer(wait_time, func)
        self._timers.append(timer)
        timer.start()

    def stop(self) -> None:
        if not self._is_running.is_set():
            raise ValueError(f"stopped but behavior {self.__class__} is not running ")

        while self._children:
            child = self._children.pop()
            child.stop()

        for timer in self._timers:
            timer.cancel()
        self._timers.clear()

        self._is_running.clear()
        if self.parent and self in self.parent._children:
            self.parent._children.remove(self)

        Logger().info(f"Stopped {self.__class__}")
        self.event_manager.clear_listener_by_origin(self)

    def finish(self, error_code: str | None = None) -> None:
        if error_code:
            Logger().warning(
                f"Stopping {self.__class__} with error code : {error_code}"
            )
        self.stop()
        if self.callback:
            callback = self.callback
            self.callback = None
            callback(error_code)
