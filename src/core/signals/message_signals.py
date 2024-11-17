from PyQt5.QtCore import QObject, pyqtSignal


class MessageInfoSignals(QObject):
    msg_info = pyqtSignal(object, bool)
    clear_msg_infos = pyqtSignal()
