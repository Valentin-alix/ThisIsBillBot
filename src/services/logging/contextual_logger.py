from dataclasses import dataclass, field
from functools import cached_property

from src.services.logging.logger import Logger


@dataclass
class ContextualLogger:
    _logger: Logger
    _contextual_logger: Logger | None = field(init=False, default=None)

    @cached_property
    def logger(self) -> Logger:
        if self._contextual_logger is None:
            self._contextual_logger = Logger(
                log_signals=self._logger.log_signals,
                title=self._logger.title,
                context=self.__class__.__name__,
            )
        return self._contextual_logger
