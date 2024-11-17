import logging
from typing import Any

from src.core.signals.log_signals import LogSignals
from src.services.logging.log_level import LogLevel


class Logger(logging.Logger):
    def __init__(
        self, log_signals: LogSignals, title: str = "root", context: str | None = None
    ) -> None:
        super().__init__(name=title)
        self.title = title
        self.context = context
        self.log_signals = log_signals
        self.setLevel(logging.DEBUG)
        self.addHandler(logging.NullHandler())

    def _get_log_msg(self, msg: Any) -> str:
        if self.context:
            return f"[{self.context}] {msg}"
        return msg

    def debug(self, msg: Any, *args, **kwargs):
        if self.level <= logging.DEBUG:
            formatted_msg = self._get_log_msg(msg)
            self.log_signals.log_emitted.emit(LogLevel.DEBUG, formatted_msg)
            super().debug(formatted_msg, *args, **kwargs)

    def info(self, msg: Any, *args, **kwargs):
        if self.level <= logging.INFO:
            formatted_msg = self._get_log_msg(msg)
            self.log_signals.log_emitted.emit(LogLevel.INFO, formatted_msg)
            super().info(formatted_msg, *args, **kwargs)

    def warning(self, msg: Any, *args, **kwargs):
        if self.level <= logging.WARNING:
            formatted_msg = self._get_log_msg(msg)
            self.log_signals.log_emitted.emit(LogLevel.WARNING, formatted_msg)
            super().warning(formatted_msg, *args, **kwargs)

    def error(self, msg: Any, *args, **kwargs):
        if self.level <= logging.ERROR:
            formatted_msg = self._get_log_msg(msg)
            self.log_signals.log_emitted.emit(LogLevel.ERROR, formatted_msg)
            super().error(formatted_msg, *args, **kwargs)

    def critical(self, msg: Any, *args, **kwargs):
        if self.level <= logging.CRITICAL:
            formatted_msg = self._get_log_msg(msg)
            self.log_signals.log_emitted.emit(LogLevel.CRITICAL, formatted_msg)
            super().critical(msg, *args, **kwargs)
