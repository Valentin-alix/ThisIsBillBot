import logging

from src import const
from src.core.signals.log_signals import LogSignals
from src.services.debug_recorder import DebugRecorder, DebugRecorderLogHandler
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

    def __init__(
        self,
        log_signals: LogSignals,
        title: str,
        debug_recorder: DebugRecorder,
    ) -> None:
        super().__init__(name=title)
        self.title = title
        self.log_signals = log_signals

        filter = ContextFallbackFilter()
        self.addFilter(filter)

        self.debug_recorder_handler = DebugRecorderLogHandler(debug_recorder)
        self.debug_recorder_handler.setFormatter(logging.Formatter("[%(context)s] %(message)s"))
        self.addHandler(self.debug_recorder_handler)

        self.gui_formatter = logging.Formatter("[%(context)s] - %(message)s")
        if const.DEBUG:
            self.log_signal_handler = LogSignalHandler(log_signals)
            self.log_signal_handler.setFormatter(self.gui_formatter)
            self.addHandler(self.log_signal_handler)
