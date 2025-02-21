import logging
import os
from logging.handlers import RotatingFileHandler

from src.const import LOG_FOLDER
from src.core.signals.log_signals import LogSignals
from src.services.logging_utils.filters import ContextFallbackFilter
from src.services.logging_utils.handlers import LogSignalHandler


def configure_root_logger() -> logging.Logger:
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    stream_handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - [GLOBAL] %(message)s")
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    return logger


def init_root_gui_logging(signals: LogSignals) -> logging.Logger:
    logger = logging.getLogger()
    log_signal_handler = LogSignalHandler(signals)
    formatter = logging.Formatter("[GLOBAL] %(message)s")
    log_signal_handler.setFormatter(formatter)
    logger.addHandler(log_signal_handler)
    return logger


class BotLogger(logging.Logger):
    """specific bot logger, title is only used for filename"""

    def __init__(self, log_signals: LogSignals, title: str) -> None:
        super().__init__(name=title)
        self.title = title
        self.log_signals = log_signals

        filter = ContextFallbackFilter()
        self.addFilter(filter)

        file_handler = RotatingFileHandler(
            f"{os.path.join(LOG_FOLDER, title)}.log",
            maxBytes=1024 * 1024 * 1024,
            backupCount=1,
        )
        self.formatter = logging.Formatter(
            "%(asctime)s - [%(context)s] %(levelname)s - %(message)s"
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(self.formatter)
        self.addHandler(file_handler)

        self.gui_formatter = logging.Formatter("[%(context)s] - %(message)s")
        self.log_signal_handler = LogSignalHandler(log_signals)
        self.log_signal_handler.setFormatter(self.gui_formatter)
        self.addHandler(self.log_signal_handler)
