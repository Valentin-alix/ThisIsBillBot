from PyQt5.QtCore import QObject, pyqtSignal


class BotSignals(QObject):
    play_harvester = pyqtSignal(object, object)
    play_fighter = pyqtSignal(object, object)
    play_auto_bot = pyqtSignal(object, object)
    play_crafter = pyqtSignal(object)
    play_mule_kamas = pyqtSignal()
    play_usable_behavior = pyqtSignal(str)
    play = pyqtSignal(bool)
    stop = pyqtSignal()
