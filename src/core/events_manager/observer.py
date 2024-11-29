from dataclasses import dataclass
from typing import Callable, Generic, ParamSpec

P = ParamSpec("P")


@dataclass(frozen=True)
class Observer(Generic[P]):
    callback: Callable[P, None]
    originator: object
    once: bool
