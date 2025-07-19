from collections.abc import Callable
from dataclasses import dataclass
from typing import TypeVar

from google.protobuf.message import Message

T = TypeVar("T", bound=Message)


@dataclass
class Modifier[T]:
    callback: Callable[[T], T | None]
    originator: object
