from PyQt5.QtCore import QObject, pyqtSignal

from src.interfaces.models.message_info import MessageInfo


class MessageInfoSignals(QObject):
    message_info = pyqtSignal(MessageInfo)
