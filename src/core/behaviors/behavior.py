from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from threading import Event, Timer
from typing import Callable

from src.common.logger import Logger
from src.common.timing import get_random_range
from src.event_manager import EventManager


class EndCode(Enum):
    STOPPED = auto()
    SUCCESS = auto()
    ERROR = auto()


@dataclass
class Behavior(ABC):
    event_manager: EventManager
    is_running: Event = field(init=False, default_factory=Event)
    callback: Callable[[EndCode], None] | None = field(init=False, default=None)
    children: "list[Behavior]" = field(init=False, default_factory=list)
    parent: "Behavior|None" = field(init=False, default=None)

    _timers: list[Timer] = field(init=False, default_factory=list)

    def start(
        self,
        callback: Callable | None,
        parent: "Behavior|None",
        *args,
        **kwargs,
    ):
        Logger().info(f"starting : {self.__class__}")
        if parent and not parent.is_running.is_set():
            Logger().warning(
                f"starting behavior {self.__class__} but parent {parent.__class__} is not running"
            )
            return
        if self.is_running.is_set():
            Logger().warning(
                f"starting behavior {self.__class__} but it is already running"
            )
            return
        self.parent = parent
        if self.parent:
            self.parent.children.append(self)
        self.is_running.set()
        self.callback = callback
        self.run(*args, **kwargs)

    @abstractmethod
    def run(self, *args, **kwargs): ...

    def stop(self):
        while self.children:
            child = self.children.pop()
            child.stop()
        self.finish(EndCode.STOPPED)

    def run_fn_future(self, range_time: tuple[float, float], func: Callable):
        wait_time = get_random_range(range_time)
        Logger().info(f"Waiting for {wait_time} before executing {func.__name__}")
        timer = Timer(wait_time, func)
        self._timers.append(timer)
        timer.start()

    def finish(self, code: EndCode = EndCode.SUCCESS):
        if not self.is_running.is_set():
            Logger().warning(
                f"finish emitted but behavior {self.__class__} is not running "
            )
            return

        for timer in self._timers:
            timer.cancel()
        self._timers.clear()

        self.is_running.clear()
        if self.parent and self in self.parent.children:
            self.parent.children.remove(self)
        Logger().info(f"Finishing {self.__class__} code : {code}")
        self.event_manager.clear_listener_by_origin(self)

        callback = self.callback
        self.callback = None
        if callback and code is not EndCode.STOPPED:
            callback(code)
