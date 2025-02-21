import logging
from enum import IntEnum


class LogLevel(IntEnum):
    """logging have no level Enum, we need this to show corresponding level name in gui"""

    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL
