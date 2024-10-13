from PyQt5.QtCore import QObject, pyqtSignal


class BotSignals(QObject):
    play_harvester = pyqtSignal(object, object)
    play_crafter = pyqtSignal(object)
    play = pyqtSignal()
    stop = pyqtSignal()
