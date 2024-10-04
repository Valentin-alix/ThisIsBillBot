from PyQt5.QtCore import QObject, pyqtSignal


class HarvesterSignals(QObject):
    play = pyqtSignal()
    stop = pyqtSignal()
