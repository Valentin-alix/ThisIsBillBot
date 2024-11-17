from PyQt5.QtCore import QObject, pyqtSignal

from src.services.logging.log_level import LogLevel


class LogSignals(QObject):
    log_emitted = pyqtSignal(LogLevel, str)
