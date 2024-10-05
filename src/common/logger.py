import logging
import sys
from typing import Any

import coloredlogs

from src.interfaces.metaclasses.singleton import Singleton


class Logger(logging.Logger, metaclass=Singleton):
    def __init__(self, title: str | None = None) -> None:
        super().__init__(name=title if title else "root")
        self.title = title
        self.setLevel(logging.DEBUG)
        coloredlogs.install(
            level=logging.DEBUG,
            logger=self,
            isatty=True,
            stream=sys.stdout,
            fmt="%(asctime)s %(levelname)-8s %(message)s",
        )

    def _get_log_msg(self, msg: Any) -> str:
        if not self.title:
            return msg
        return f"{self.title}: {msg}"

    def debug(self, msg: Any, *args, **kwargs):
        super().debug(self._get_log_msg(msg), *args, **kwargs)

    def info(self, msg: Any, *args, **kwargs):
        super().info(self._get_log_msg(msg), *args, **kwargs)

    def warning(self, msg: Any, *args, **kwargs):
        super().warning(self._get_log_msg(msg), *args, **kwargs)

    def error(self, msg: Any, *args, **kwargs):
        super().error(self._get_log_msg(msg), *args, **kwargs)

    def critical(self, msg: Any, *args, **kwargs):
        super().critical(self._get_log_msg(msg), *args, **kwargs)
