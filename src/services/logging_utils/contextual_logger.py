from abc import ABC
from collections.abc import MutableMapping
from dataclasses import dataclass
from functools import cached_property
from logging import LoggerAdapter
from typing import Any, cast

from src.services.logging_utils.loggers import BotLogger


class ContextLoggerAdapter(LoggerAdapter):
    def process(self, msg: str, kwargs: MutableMapping[str, Any]):
        extra: dict[str, Any] = kwargs.get("extra", {})
        if self.extra:
            extra = {**self.extra, **extra}
        kwargs["extra"] = extra
        return msg, kwargs


@dataclass
class ContextualLogger(ABC):
    _logger: BotLogger

    @cached_property
    def logger(self):
        return cast(
            BotLogger,
            ContextLoggerAdapter(self._logger, {"context": self.__class__.__name__}),
        )
