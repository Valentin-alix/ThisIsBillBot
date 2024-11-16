from dataclasses import dataclass
from typing import Callable, ParamSpec, Generic

P = ParamSpec("P")


@dataclass(frozen=True)
class Observer(Generic[P]):
    callback: Callable[P, None]
    originator: object
    once: bool
