from dataclasses import dataclass, field
from threading import RLock
from typing import Callable


@dataclass
class SubjectBarrier:
    """custom barrier, wait for target count before executing observers"""

    _lock: RLock = field(init=False, default_factory=RLock)
    current_count: int = field(init=False, default=0)
    target_count: int | None = field(init=False, default=None)

    _callbacks: list[tuple[Callable[[], None], object]] = field(
        init=False, default_factory=list
    )

    def set_target(self, target_count: int):
        with self._lock:
            self.target_count = target_count
            if self.target_count >= self.current_count:
                self.process_callbacks()

    def process_callbacks(self):
        with self._lock:
            _callbacks = self._callbacks[::]
            self._callbacks.clear()
            self.current_count = 0
            for callback, originator in _callbacks:
                callback()

    def clear_by_originator(self, originator: object):
        with self._lock:
            self._callbacks = [
                (callback, _originator)
                for callback, _originator in self._callbacks
                if _originator != originator
            ]

    def on_ready(
        self,
        originator: object,
        callback: Callable[[], None] | None = None,
    ):
        with self._lock:
            if callback is not None:
                self._callbacks.append((callback, originator))
            if self.target_count is None:
                raise ValueError("Target count not set.")
            self.current_count += 1
            if self.current_count >= self.target_count:
                self.process_callbacks()
