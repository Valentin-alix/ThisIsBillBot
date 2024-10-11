from PyQt5.QtCore import QObject, pyqtSignal

from src.interfaces.models.message import MessageInfo


class MessageInfoSignals(QObject):
    msg_info = pyqtSignal(MessageInfo, bool)
