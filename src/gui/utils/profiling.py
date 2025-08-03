import functools
import threading
from collections.abc import Callable
from time import perf_counter
from typing import Final, ParamSpec, TypeVar

from PyQt6.QtCore import QEvent, QObject
from PyQt6.QtWidgets import QApplication

P = ParamSpec("P")
R = TypeVar("R")

EVENT_NAMES = {value: name for name, value in vars(QEvent).items() if isinstance(value, int)}

PROFILING_ENABLED: Final = False


def profiled_slot(func: Callable[P, R], threshold_ms: int = 1) -> Callable[P, R]:
    if not PROFILING_ENABLED:
        return func

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        start = perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            dt = (perf_counter() - start) * 1000
            if dt >= threshold_ms:
                print(f"[SLOT] {func.__qualname__} | {dt:.2f} ms | {threading.current_thread().name}")

    return wrapper


class ProfiledApp(QApplication):
    def notify(self, a0: QObject | None, a1: QEvent | None) -> bool:
        start = perf_counter()
        try:
            return super().notify(a0, a1)
        finally:
            duration = perf_counter() - start
            self._profile_event(a0, a1, duration)

    def _profile_event(
        self,
        receiver: QObject | None,
        event: QEvent | None,
        duration: float,
    ) -> None:
        if receiver is None or event is None:
            return
        if duration > 0.5:
            event_name = EVENT_NAMES.get(event.type(), str(event.type()))
            if hasattr(receiver, "objectName"):
                try:
                    name = receiver.objectName() or receiver.__class__.__name__
                except RuntimeError:
                    name = receiver.__class__.__name__
            else:
                name = receiver.__class__.__name__
            print(f"{name} | {event_name} | {duration * 1000:.2f} ms")
