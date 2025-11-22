import threading
from collections import deque
from dataclasses import dataclass
from datetime import datetime

from PyQt6.QtCore import QObject

from src.services.logging_utils.log_level import LogLevel


@dataclass(frozen=True, slots=True)
class RecentLogEntry:
    sequence: int
    logged_at: datetime
    level: LogLevel
    message: str


class LogSignals(QObject):
    def __init__(self) -> None:
        super().__init__()
        self._entries: deque[RecentLogEntry] = deque(maxlen=5000)
        self._lock = threading.Lock()
        self._latest_sequence = 0

    @property
    def latest_sequence(self) -> int:
        with self._lock:
            return self._latest_sequence

    def publish(self, level: LogLevel, message: str, logged_at: datetime) -> None:
        with self._lock:
            self._latest_sequence += 1
            self._entries.append(RecentLogEntry(self._latest_sequence, logged_at, level, message))

    def recent_after(self, sequence: int) -> tuple[int, list[RecentLogEntry]]:
        with self._lock:
            return (
                self._latest_sequence,
                [entry for entry in self._entries if entry.sequence > sequence],
            )
