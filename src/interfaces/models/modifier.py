from dataclasses import dataclass
from typing import Callable, TypeVar

from google.protobuf.message import Message

T = TypeVar("T", bound=Message)


@dataclass
class Modifier:
    callback: Callable[[T], T | None]
    originator: object
