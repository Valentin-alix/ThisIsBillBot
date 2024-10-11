from PyQt5.QtCore import QObject, pyqtSignal

from src.interfaces.enums.log_level import LogLevel


class LogSignals(QObject):
    log_emitted = pyqtSignal(LogLevel, str)
