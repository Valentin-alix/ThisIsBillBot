from PyQt5.QtCore import QObject, pyqtSignal


class SharedSignals(QObject):
    launch_account = pyqtSignal(str)
