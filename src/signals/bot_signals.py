from PyQt5.QtCore import QObject, pyqtSignal


class BotSignals(QObject):
    play_harvester = pyqtSignal(object, object)
    play_crafter = pyqtSignal(object)
    play_mule = pyqtSignal(int, int)
    play = pyqtSignal()
    stop = pyqtSignal()
