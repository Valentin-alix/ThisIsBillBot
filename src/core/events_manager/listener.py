from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from threading import Timer
from typing import TypeVar

from google.protobuf.message import Message

from src.core.events_manager.priority import PriorityEnum
from src.services.logging_utils.loggers import BotLogger

T = TypeVar("T", bound=Message)


@dataclass
class Listener[T]:
    msg_type: type[T]
    callback: Callable[[T], None]
    originator: object
    logger: BotLogger
    once: bool = field(default=False)
    priority: int = field(default=PriorityEnum.NORMAL)
    timeout: float | None = None
    on_timeout: Callable[[], None] | None = None

    _deleted: bool = field(init=False, default=False)
    _timeout_timer: Timer | None = field(init=False, default=None)
    _context: str = field(init=False, default="")
    registered_at: datetime = field(init=False, default_factory=datetime.now)

    def __post_init__(self) -> None:
        self._context = f"{self.originator.__class__.__name__}:{self.msg_type.__name__}"
        if self.timeout is not None and self.on_timeout is not None:
            self._timeout_timer = Timer(
                interval=self.timeout, function=self.on_timeout_callback
            )
            self._timeout_timer.start()

    def on_timeout_callback(self) -> None:
        if self._deleted:
            self.logger.info(
                f"{self._context} : On timeout callback called but listener is deleted"
            )
            return
        if self.on_timeout is None:
            raise ValueError("timeout timer is set but no timeout callback provided")
        self.logger.info(f"{self._context} : Calling on timeout")
        self.on_timeout()

    def delete(self) -> None:
        if self._deleted:
            raise ValueError("listener is already deleted !")
        if self._timeout_timer is not None:
            self._timeout_timer.cancel()
        self._deleted = True

    def __lt__(self, other: "Listener[T]") -> bool:
        return self.priority < other.priority

    def __hash__(self) -> int:
        return id(self)
