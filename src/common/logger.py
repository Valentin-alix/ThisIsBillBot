import logging
from typing import Any

from src.interfaces.enums.log_level import LogLevel
from src.signals.log_signals import LogSignals


class Logger(logging.Logger):
    def __init__(self, log_signals: LogSignals, title: str | None = None) -> None:
        super().__init__(name=title if title else "root")
        self.title = title
        self.log_signals = log_signals
        self.setLevel(logging.ERROR)

    def _get_log_msg(self, msg: Any) -> str:
        if not self.title:
            return msg
        return f"{self.title}: {msg}"

    def debug(self, msg: Any, *args, **kwargs):
        self.log_signals.log_emitted.emit(LogLevel.DEBUG, msg)
        msg = self._get_log_msg(msg)
        super().debug(msg, *args, **kwargs)

    def info(self, msg: Any, *args, **kwargs):
        self.log_signals.log_emitted.emit(LogLevel.INFO, msg)
        msg = self._get_log_msg(msg)
        super().info(msg, *args, **kwargs)

    def warning(self, msg: Any, *args, **kwargs):
        self.log_signals.log_emitted.emit(LogLevel.WARNING, msg)
        msg = self._get_log_msg(msg)
        super().warning(msg, *args, **kwargs)

    def error(self, msg: Any, *args, **kwargs):
        self.log_signals.log_emitted.emit(LogLevel.ERROR, msg)
        msg = self._get_log_msg(msg)
        super().error(msg, *args, **kwargs)

    def critical(self, msg: Any, *args, **kwargs):
        self.log_signals.log_emitted.emit(LogLevel.CRITICAL, msg)
        msg = self._get_log_msg(msg)
        super().critical(msg, *args, **kwargs)
