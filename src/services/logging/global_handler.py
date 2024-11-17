import logging

from src.core.signals.global_log_signals import GlobalLogSignals
from src.services.logging.log_level import LogLevel


class GlobalSignalHandler(logging.Handler):
    def __init__(self, signals: GlobalLogSignals):
        super().__init__()
        self._signals = signals

    def emit(self, record: logging.LogRecord):
        msg = self.format(record)
        self._signals.log_emitted.emit(LogLevel(record.levelno), msg)
