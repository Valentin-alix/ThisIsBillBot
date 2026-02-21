from PyQt6.QtCore import QObject, pyqtSignal


class BotSignals(QObject):
    play_harvester = pyqtSignal(object, object)
    play_fighter = pyqtSignal(object, object)
    play_auto_bot = pyqtSignal()
    play_crafter = pyqtSignal(object)
    play_usable_behavior = pyqtSignal(str)
    play = pyqtSignal(bool)
    stop = pyqtSignal()
    disconnect_runtime = pyqtSignal()
