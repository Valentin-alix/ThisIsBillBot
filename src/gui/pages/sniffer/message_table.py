from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidgetItem
from qfluentwidgets import TableView, TableWidget

from src.gui.components.table import BaseTableWidget, ColumnInfo
from src.gui.signals.msg_signals import MessageSignals
from src.models.message_info import MessageInfo


class MessageTable(BaseTableWidget):
    def __init__(self, msg_signals: MessageSignals, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.msg_signals = msg_signals
        columns: list[ColumnInfo] = [
            ColumnInfo(name="Heure"),
            ColumnInfo(name="Serveur"),
            ColumnInfo(name="Type"),
            ColumnInfo(name="Message"),
        ]
        self.set_columns(columns)
        metadata_col_index = self.table.columnCount()
        self.table.setColumnCount(metadata_col_index + 1)
        self.table.setColumnHidden(metadata_col_index, True)

        self.table.setEditTriggers(TableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(TableView.SelectRows)
        self.msg_signals.received_msg_info.connect(self.add_row)

    def add_row(self, msg_info: MessageInfo):
        table_index = self.table.rowCount()
        self.table.setRowCount(self.table.rowCount() + 1)

        self.table.setItem(
            table_index,
            0,
            QTableWidgetItem(msg_info.received_time.strftime("%H:%M:%S")),
        )
        self.table.setItem(table_index, 1, QTableWidgetItem(msg_info.server_type))
        self.table.setItem(table_index, 2, QTableWidgetItem(msg_info.msg_type))
        self.table.setItem(table_index, 3, QTableWidgetItem(msg_info.msg_content_type))

        table_widget_item = QTableWidgetItem()
        table_widget_item.setData(Qt.UserRole, msg_info.msg_json)
        self.table.setItem(table_index, 4, table_widget_item)
