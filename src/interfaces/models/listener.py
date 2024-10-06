from dataclasses import dataclass, field
from threading import Timer
from typing import Callable, TypeVar, Type

from google.protobuf.message import Message

from src.common.logger import Logger
from src.interfaces.enums.priority import PriorityEnum

T = TypeVar("T", bound=Message)


@dataclass
class Listener:
    msg_type: Type[T]
    callback: Callable[[T], None]
    originator: object
    once: bool = field(default=False)
    priority: int = field(default=PriorityEnum.NORMAL)
    timeout: float | None = None
    on_timeout: Callable | None = None

    _deleted: bool = field(init=False, default=False)
    _timeout_timer: Timer | None = field(init=False, default=None)

    def __post_init__(self):
        if self.timeout and self.on_timeout is not None:
            if self.on_timeout is None:
                raise ValueError(f"timeout is defined but not function on_timeout !")
            if self._deleted:
                raise ValueError(
                    "listener was going to use timeout callback but it is deleted !"
                )
            self._timeout_timer = Timer(
                interval=self.timeout, function=self.on_timeout_callback
            )
            self._timeout_timer.start()

    def on_timeout_callback(self):
        Logger().info(f"Sending on timeout callback : {self.on_timeout.__name__}")
        self.on_timeout()

    def delete(self):
        if self._deleted:
            raise ValueError("listener is already deleted !")
        if self._timeout_timer is not None:
            self._timeout_timer.cancel()

    def __lt__(self, other: "Listener") -> bool:
        return self.priority < other.priority
