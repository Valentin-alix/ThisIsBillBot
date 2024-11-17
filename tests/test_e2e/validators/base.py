from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from google.protobuf.message import Message


@dataclass
class ValidationResult:
    is_valid: bool
    reason: str | None = None
    details: dict[str, Any] | None = None


@dataclass
class RecordedMessage:
    msg: Message
    timestamp: float
    from_server: bool
    msg_type_name: str


class SequenceValidator(ABC):

    @abstractmethod
    def validate(self, messages: list[RecordedMessage]) -> list[ValidationResult]:
        pass

    @abstractmethod
    def applies_to(self, messages: list[RecordedMessage]) -> bool:
        pass
