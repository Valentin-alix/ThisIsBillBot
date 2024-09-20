from PyQt5.QtCore import QObject, pyqtSignal

from src.models.message_info import MessageInfo


class MessageSignals(QObject):
    received_msg_info = pyqtSignal(MessageInfo)
