import logging


class ContextFallbackFilter(logging.Filter):
    """just a filter to populate context with funcName in case we don't use the logger in ContextualLogger"""

    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "context"):
            record.context = record.funcName
        return True
