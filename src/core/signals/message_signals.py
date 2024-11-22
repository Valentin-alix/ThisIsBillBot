from PyQt6.QtCore import QObject, pyqtSignal


class MessageInfoSignals(QObject):
    msg_info = pyqtSignal(object, bool)
