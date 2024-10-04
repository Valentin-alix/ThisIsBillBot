from PyQt5.QtCore import QObject, pyqtSignal


class StatePropertySignals(QObject):
    property_set_by_class = pyqtSignal(str, str, str)


class PlayerSignals(QObject):
    connected = pyqtSignal()
    disconnected = pyqtSignal()
