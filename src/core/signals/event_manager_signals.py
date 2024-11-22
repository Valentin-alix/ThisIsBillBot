from PyQt6.QtCore import QObject, pyqtSignal


class EventManagerSignals(QObject):
    listeners_added = pyqtSignal(list)
    listeners_removed = pyqtSignal(list)
