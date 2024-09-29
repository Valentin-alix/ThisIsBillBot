from PyQt5.QtCore import QObject, pyqtSignal


class AccountSignals(QObject):
    account_is_connected = pyqtSignal(bool)
    character_connection = pyqtSignal(str)
