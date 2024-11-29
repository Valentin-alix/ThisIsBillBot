import logging
import os
from logging.handlers import RotatingFileHandler
from types import TracebackType
from collections.abc import Mapping

from src.const import LOG_FOLDER
from src.core.signals.global_log_signals import GlobalLogSignals
from src.core.signals.log_signals import LogSignals
from src.services.logging.global_handler import GlobalSignalHandler
from src.services.logging.log_level import LogLevel


def init_global_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - [GLOBAL] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def init_gui_global_logging(signals: GlobalLogSignals):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    handler = GlobalSignalHandler(signals)
    formatter = logging.Formatter("[GLOBAL] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)


class Logger(logging.Logger):
    def __init__(self, log_signals: LogSignals, title: str) -> None:
        super().__init__(name=title)
        self.title = title
        self.log_signals = log_signals

        file_handler = RotatingFileHandler(
            f"{os.path.join(LOG_FOLDER, title)}.log",
            maxBytes=1024 * 1024 * 1024,
            backupCount=1,
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(file_formatter)
        self.addHandler(file_handler)

    def log(
        self,
        level: int,
        msg: object,
        *args: object,
        exc_info: bool | BaseException | tuple[type[BaseException], BaseException, TracebackType | None] | tuple[None, None, None] | None = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: Mapping[str, object] | None = None,
    ) -> None:
        self.log_signals.log_emitted.emit(LogLevel(level), msg)
        return super().log(
            level,
            str(msg),
            *args,
            exc_info=exc_info,
            stack_info=stack_info,
            stacklevel=stacklevel,
            extra=extra,
        )
