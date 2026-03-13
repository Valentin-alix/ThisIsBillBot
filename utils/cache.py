import functools
import inspect
from collections.abc import Callable


def cache[T](func: Callable[..., T]) -> Callable[..., T]:
    wrapper = functools.cache(func)
    object.__setattr__(wrapper, "__signature__", inspect.signature(func))
    return wrapper
