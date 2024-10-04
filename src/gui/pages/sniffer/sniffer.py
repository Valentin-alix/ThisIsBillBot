from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import QHBoxLayout, QSplitter
from qfluentwidgets import PivotItem

from src.gui.pages.sniffer.message_detail import MessageDetailWidget
from src.gui.pages.sniffer.message_table import MessageTable
from src.interfaces.models.message_info import MessageInfo
from src.signals.message_signals import MessageInfoSignals


class SnifferWidget(PivotItem):
    def __init__(self, message_info_signals: MessageInfoSignals, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.m_layout = QHBoxLayout()
        self.setLayout(self.m_layout)

        self.msg_table = MessageTable(message_info_signals)
        self.msg_table.table_content.table.cellClicked.connect(self.on_click_msg)

        self.msg_detail = MessageDetailWidget()
        self.msg_detail.hide()
        self.msg_detail.quit_btn.clicked.connect(self.on_close_detail)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.msg_table)
        splitter.addWidget(self.msg_detail)

        self.layout().addWidget(splitter)

    @pyqtSlot(int)
    def on_click_msg(self, row: int):
        if (msg_item := self.msg_table.table_content.table.item(row, 4)) is None:
            return
        msg_infos: MessageInfo = msg_item.data(Qt.UserRole)
        self.msg_detail.set_content(msg_infos.msg_json, msg_infos.raw_content)
        self.msg_detail.show()

    @pyqtSlot()
    def on_close_detail(self):
        self.msg_detail.hide()
