from PyQt5.QtCore import QObject, pyqtSignal


class SharedFarmSignals(QObject):
    play_fighter = pyqtSignal(int, object, object, object)
    play_mule = pyqtSignal(int, int)
