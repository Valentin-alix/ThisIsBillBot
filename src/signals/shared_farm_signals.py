from PyQt5.QtCore import QObject, pyqtSignal


class SharedSignals(QObject):
    play_fighter = pyqtSignal(int, object, object, object)
    launch_account = pyqtSignal(str)
