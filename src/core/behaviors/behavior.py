from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from threading import Event
from typing import Callable

from src.common.logger import Logger
from src.event_manager import EventManager


@dataclass
class Behavior(ABC):
    event_manager: EventManager
    is_running: Event = field(init=False, default_factory=Event)
    callback: Callable | None = field(init=False, default=None)
    children: "list[Behavior]" = field(init=False, default_factory=list)

    def start(
        self, callback: Callable | None, parent: "Behavior|None" = None, *args, **kwargs
    ):
        Logger().info(f"starting : {self.__class__.__name__}")
        if parent and not parent.is_running.is_set():
            raise ValueError(
                f"starting behavior {self.__class__.__name__} but parent is not running"
            )
        if self.is_running.is_set():
            raise ValueError(
                f"starting behavior {self.__class__.__name__} but it is already running"
            )
        if parent:
            parent.children.append(self)
        self.is_running.set()
        self.callback = callback
        self.run(*args, **kwargs)

    def stop(self):
        while self.children:
            child = self.children.pop()
            child.stop()
        self.is_running.clear()
        self.finish(False)

    @abstractmethod
    def run(self, *args, **kwargs): ...

    def finish(self, success: bool = True):
        if not self.is_running.is_set():
            raise ValueError(
                f"finish emitted but behavior {self.__class__.__name__} is not running "
            )
        Logger().info(
            f"Finishing {self.__class__.__name__} success : {"Yes" if success else "No"}"
        )
        self.event_manager.clear_listener_by_origin(self)
        self.is_running.clear()

        callback = self.callback
        self.callback = None
        if callback and success:
            callback()
