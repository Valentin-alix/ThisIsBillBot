import datetime

from PyQt5.QtCore import QObject, pyqtSignal


class GameInfoSignals(QObject):
    connected = pyqtSignal()
    disconnected = pyqtSignal()
    is_ready_to_play = pyqtSignal()
    inventory_weight = pyqtSignal(int)
    weight_max = pyqtSignal(int)
    breed_id = pyqtSignal(int)
    character_id = pyqtSignal(object)
    character_name = pyqtSignal(str)
    subscription_end_date = pyqtSignal(datetime.datetime)
    in_fight = pyqtSignal(bool)
    level = pyqtSignal(int)
    team = pyqtSignal(object)
    fight_turn = pyqtSignal(int)
    kamas = pyqtSignal(int)
