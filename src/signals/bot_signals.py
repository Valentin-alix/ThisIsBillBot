from PyQt5.QtCore import QObject, pyqtSignal


class BotSignals(QObject):
    play_harvester = pyqtSignal(object, object)
    play_fighter = pyqtSignal(object, object, object)
    play_crafter = pyqtSignal(object)
    play_mule_kamas = pyqtSignal()
    play = pyqtSignal()
    stop = pyqtSignal()
