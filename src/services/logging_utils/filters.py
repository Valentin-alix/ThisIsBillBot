import logging


class ContextFallbackFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "context"):
            record.context = record.funcName
        return True
