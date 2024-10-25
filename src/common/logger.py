import logging
from logging.handlers import RotatingFileHandler
import os.path
from pathlib import Path
from typing import Any
from src.interfaces.enums.log_level import LogLevel
from src.signals.log_signals import LogSignals

LOG_FOLDER = os.path.join(Path(__file__).parent.parent.parent, "resources", "logs")


class Logger(logging.Logger):
    def __init__(self, log_signals: LogSignals, title: str = "root") -> None:
        super().__init__(name=title)
        self.title = title
        self.log_signals = log_signals
        self.setLevel(logging.DEBUG)

        file_handler = RotatingFileHandler(
            f"{os.path.join(LOG_FOLDER, title)}.log",
            maxBytes=100_000_000,
            backupCount=1,
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(file_formatter)
        self.addHandler(file_handler)

    def _get_log_msg(self, msg: Any) -> str:
        return msg

    def debug(self, msg: Any, *args, **kwargs):
        if self.level <= logging.DEBUG:
            self.log_signals.log_emitted.emit(LogLevel.DEBUG, msg)
            msg = self._get_log_msg(msg)
            super().debug(msg, *args, **kwargs)

    def info(self, msg: Any, *args, **kwargs):
        if self.level <= logging.INFO:
            self.log_signals.log_emitted.emit(LogLevel.INFO, msg)
            msg = self._get_log_msg(msg)
            super().info(msg, *args, **kwargs)

    def warning(self, msg: Any, *args, **kwargs):
        if self.level <= logging.WARNING:
            self.log_signals.log_emitted.emit(LogLevel.WARNING, msg)
            msg = self._get_log_msg(msg)
            super().warning(msg, *args, **kwargs)

    def error(self, msg: Any, *args, **kwargs):
        if self.level <= logging.ERROR:
            self.log_signals.log_emitted.emit(LogLevel.ERROR, msg)
            msg = self._get_log_msg(msg)
            super().error(msg, *args, **kwargs)

    def critical(self, msg: Any, *args, **kwargs):
        if self.level <= logging.CRITICAL:
            self.log_signals.log_emitted.emit(LogLevel.CRITICAL, msg)
            msg = self._get_log_msg(msg)
            super().critical(msg, *args, **kwargs)
