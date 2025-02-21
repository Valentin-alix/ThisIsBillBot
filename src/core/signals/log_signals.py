from PyQt6.QtCore import QObject, pyqtSignal

from src.services.logging_utils.log_level import LogLevel


class LogSignals(QObject):
    log_emitted = pyqtSignal(LogLevel, str)
