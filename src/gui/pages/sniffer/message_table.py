from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidgetItem
from qfluentwidgets import TableView, TableWidget

from src.gui.components.table import BaseTableWidget, ColumnInfo

from src.signals.message_signals import MessageInfoSignals
from src.interfaces.models.message_info import MessageInfo


class MessageTable(BaseTableWidget):
    def __init__(self, msg_info_signals: MessageInfoSignals, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.msg_info_signals = msg_info_signals
        columns: list[ColumnInfo] = [
            ColumnInfo(name="Message"),
            ColumnInfo(name="Serveur"),
            ColumnInfo(name="Type"),
            ColumnInfo(name="Heure"),
            ColumnInfo(name="Message détaillé", is_hidden=True),
        ]
        self.set_columns(columns)

        self.table.setEditTriggers(TableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(TableView.SelectRows)
        self.msg_info_signals.message_info.connect(self.add_row)

    def add_row(self, msg_info: MessageInfo):
        index = self.table.rowCount()
        self.table.setRowCount(index + 1)

        self.table.setItem(
            index,
            3,
            QTableWidgetItem(msg_info.received_time.strftime("%H:%M:%S")),
        )
        self.table.setItem(index, 1, QTableWidgetItem(msg_info.server_type))
        self.table.setItem(index, 2, QTableWidgetItem(msg_info.msg_name))
        self.table.setItem(index, 0, QTableWidgetItem(msg_info.sub_msg_name))

        table_widget_item = QTableWidgetItem()
        table_widget_item.setData(Qt.UserRole, msg_info.msg_json)
        self.table.setItem(index, 4, table_widget_item)
