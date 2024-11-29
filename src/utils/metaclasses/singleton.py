from typing import Any, TypeVar, cast


T = TypeVar("T")


class Singleton(type):
    _instances: dict[type[Any], object] = {}

    def __call__(cls: type[T], *args: object, **kwargs: object) -> T:
        if cls not in Singleton._instances:
            Singleton._instances[cls] = super().__call__(*args, **kwargs)
        return cast(T, Singleton._instances[cls])
