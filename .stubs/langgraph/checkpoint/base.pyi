from typing import Generic, TypeVar

V = TypeVar("V")


class BaseCheckpointSaver(Generic[V]): ...
