import logging
from dataclasses import dataclass
from datetime import datetime

from src.services.debug_recorder.recorder import DebugRecorder


@dataclass
class DebugRecorderLogHandler(logging.Handler):
    """Forwards each log record to a `DebugRecorder` queue (no Qt signal, no
    cross-thread emit). Cheap on the calling thread."""

    recorder: DebugRecorder

    def __post_init__(self) -> None:
        logging.Handler.__init__(self)

    def emit(self, record: logging.LogRecord) -> None:
        self.recorder.record_log(
            level=record.levelname,
            message=self.format(record),
            logged_at=datetime.fromtimestamp(record.created),
        )
