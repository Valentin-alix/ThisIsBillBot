from PyQt6.QtCore import QObject, pyqtSignal


class QuarantineSignals(QObject):
    changed = pyqtSignal()


quarantine_signals = QuarantineSignals()
