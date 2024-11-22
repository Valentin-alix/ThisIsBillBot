from PyQt6.QtCore import QObject
from qfluentwidgets import pyqtSignal


class ReplaySignals(QObject):
    # Signal: (path, preserve_timing, speedup, use_obfuscated)
    replay_requested = pyqtSignal(str, bool, object, bool)
