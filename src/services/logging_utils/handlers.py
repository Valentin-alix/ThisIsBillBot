import logging
from dataclasses import dataclass
from typing import Any

from src.core.signals.log_signals import LogSignals
from src.services.logging_utils.log_level import LogLevel


@dataclass
class LogSignalHandler(logging.Handler):
    """auto emit to gui when logging msg, works for global logging & bot specific logging"""

    def __init__(self, log_signals: LogSignals, *args: Any, **kwargs: Any):
        self.signals = log_signals
        super().__init__(*args, **kwargs)

    def emit(self, record: logging.LogRecord):
        msg = self.format(record)
        self.signals.log_emitted.emit(LogLevel(record.levelno), msg)
