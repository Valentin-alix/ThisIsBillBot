from PyQt5.QtCore import QObject
from qfluentwidgets import pyqtSignal


class ReplaySignals(QObject):
    replay_requested = pyqtSignal(str)
