import functools
import threading
from collections.abc import Callable
from time import perf_counter
from typing import Final, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

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
