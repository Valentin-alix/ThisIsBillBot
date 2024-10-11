import functools
import inspect
from typing import TypeVar, Callable

T = TypeVar("T", bound=Callable)


def cache(func: T):
    wrapper = functools.cache(func)
    wrapper.__signature__ = inspect.signature(func)
    return wrapper
