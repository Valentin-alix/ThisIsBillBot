from functools import cache, wraps
from typing import Callable, TypeVar

T = TypeVar("T")


def typed_cache(func: Callable[..., T]) -> Callable[..., T]:
    @wraps(func)
    def wrapper(*args, **kwargs) -> T:
        return cache(func)(*args, **kwargs)

    return wrapper
