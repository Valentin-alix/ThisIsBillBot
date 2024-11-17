import functools
import inspect
import threading
from time import perf_counter

from PyQt5.QtCore import QEvent, QObject
from PyQt5.QtWidgets import QApplication

EVENT_NAMES = {
    value: name for name, value in vars(QEvent).items() if isinstance(value, int)
}

PROFILING_ENABLED = False


def profiled_slot(func, threshold_ms=1):
    if not PROFILING_ENABLED:
        return func

    sig = inspect.signature(func)
    params = list(sig.parameters.values())

    max_args = sum(
        p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD) for p in params
    )

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = perf_counter()
        call_args = args[:max_args]
        try:
            return func(*call_args, **kwargs)
        finally:
            dt = (perf_counter() - start) * 1000
            if dt >= threshold_ms:
                print(
                    f"[SLOT] {func.__qualname__} | "
                    f"{dt:.2f} ms | "
                    f"{threading.current_thread().name}"
                )

    return wrapper


class ProfiledApp(QApplication):
    def notify(self, receiver: QObject, event: QEvent):  # type: ignore
        start = perf_counter()
        try:
            return super().notify(receiver, event)
        finally:
            duration = perf_counter() - start
            self._profile_event(receiver, event, duration)

    def _profile_event(self, receiver, event, duration):
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
