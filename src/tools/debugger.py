import inspect
import os
import pstats
import time
from functools import wraps
from pathlib import Path
from typing import Callable


def log_caller(func: Callable):
    @wraps(func)
    def log_caller_wrapper(*args, **kwargs):
        curr_frame = inspect.currentframe()
        call_frame = inspect.getouterframes(curr_frame, 2)
        assert hasattr(func, "__name__")
        print(f"Function {func.__name__} was called by:", call_frame[1][3])
        result = func(*args, **kwargs)
        return result

    return log_caller_wrapper


def read_profile_file():
    profile = pstats.Stats(
        os.path.join(Path(__file__).parent.parent.parent, "benchmark.pstats")
    )
    profile.sort_stats("cumulative")
    profile.print_stats(50)


def timeit(func: Callable[..., object]):
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        assert hasattr(func, "__name__")
        print(f"Function {func.__name__}\t took {total_time:.4f} seconds")
        return result

    return timeit_wrapper


if __name__ == "__main__":
    path_profile = os.path.join(
        Path(__file__).parent.parent.parent, "resources", "profile.prof"
    )
    profile_stat = pstats.Stats(path_profile)
    profile_stat.sort_stats(pstats.SortKey.CUMULATIVE)
    profile_stat.print_stats("gui", 50)
