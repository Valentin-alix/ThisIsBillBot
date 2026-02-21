import functools
import inspect
from collections.abc import Callable


def cache[T](func: Callable[..., T]) -> Callable[..., T]:
    """functools.cache that preserves __signature__ for introspection tools."""
    wrapper = functools.cache(func)
    object.__setattr__(wrapper, "__signature__", inspect.signature(func))
    return wrapper
