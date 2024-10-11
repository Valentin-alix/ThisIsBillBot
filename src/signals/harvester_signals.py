from PyQt5.QtCore import QObject, pyqtSignal

from src.interfaces.enums.farm_action_enum import FarmActionEnum


class FarmActionSignals(QObject):
    play = pyqtSignal(FarmActionEnum, object, object)
    stop = pyqtSignal()
