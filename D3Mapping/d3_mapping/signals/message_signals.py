from PyQt5.QtCore import QObject, pyqtSignal

from d3_mapping.models.message import MessageInfo


class MessageInfoSignals(QObject):
    msg_info = pyqtSignal(MessageInfo, bool)
