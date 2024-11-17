from dataclasses import dataclass
from functools import cached_property
from typing import cast

from src.services.logging.context_adapter import ContextAdapter
from src.services.logging.logger import Logger


@dataclass
class ContextualLogger:
    _logger: Logger

    @cached_property
    def logger(self) -> Logger:
        return cast(
            Logger, ContextAdapter(self._logger, {"context": self.__class__.__name__})
        )
