import functools
import inspect
from typing import Callable, TypeVar

T = TypeVar("T")


def cache(func: Callable[..., T]) -> Callable[..., T]:
    wrapper = functools.cache(func)
    wrapper.__signature__ = inspect.signature(func)  # type: ignore
    return wrapper
