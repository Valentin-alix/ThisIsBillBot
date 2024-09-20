from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QWidget

from src.gui.pages.sniffer.message_detail_widget import MessageDetailWidget
from src.gui.pages.sniffer.message_table import MessageTable
from src.gui.signals.msg_signals import MessageSignals


class SnifferWidget(QWidget):
    def __init__(self, msg_signals: MessageSignals, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.m_layout = QHBoxLayout()
        self.setLayout(self.m_layout)

        self.msg_table = MessageTable(msg_signals)
        self.msg_table.table.cellClicked.connect(self.on_click_msg)

        self.msg_detail = MessageDetailWidget()
        self.msg_detail.hide()
        self.msg_detail.quit_btn.clicked.connect(self.on_close_detail)

        self.layout().addWidget(self.msg_table)
        self.layout().addWidget(self.msg_detail)

    def on_click_msg(self, row: int, _):
        if (msg_item := self.msg_table.table.item(row, 4)) is not None:
            msg_json: dict = msg_item.data(Qt.UserRole)
            self.msg_detail.set_content(msg_json)
            self.msg_detail.show()

    def on_close_detail(self):
        self.msg_detail.hide()
