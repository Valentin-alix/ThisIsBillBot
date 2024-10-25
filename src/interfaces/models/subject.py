from dataclasses import dataclass, field
from threading import _RLock as RLock
from typing import Callable, Generic, ParamSpec

from src.interfaces.models.observer import Observer

P = ParamSpec("P")


@dataclass
class Subject(Generic[P]):
    """observer pattern"""

    _lock: RLock = field(init=False, default_factory=RLock)
    _observers: list[Observer[P]] = field(init=False, default_factory=list)

    def connect(
        self, callback: Callable[P, None], originator: object, once: bool = False
    ):
        with self._lock:
            self._observers.append(
                Observer(callback=callback, originator=originator, once=once)
            )

    def disconnect_originator(self, originator: object):
        with self._lock:
            self._observers = [
                observer
                for observer in self._observers
                if observer.originator != originator
            ]

    def emit(self, *args: P.args, **kwargs: P.kwargs):
        with self._lock:
            observers = self._observers[::]
            for observer in observers:
                observer.callback(*args, **kwargs)
                if observer.once and observer in self._observers:
                    self._observers.remove(observer)
