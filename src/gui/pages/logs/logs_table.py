from datetime import datetime

from PyQt5.QtCore import pyqtSlot, QModelIndex, Qt
from PyQt5.QtGui import QStandardItem
from PyQt5.QtWidgets import QHeaderView
from qfluentwidgets import TableWidget, MessageBox

from src.gui.components.table.column_info import ColumnInfo
from src.gui.components.table.table import BaseTableWidget
from src.interfaces.enums.log_level import LogLevel


class LogsTable(BaseTableWidget):
    def __init__(self) -> None:
        super().__init__()
        columns: list[ColumnInfo] = [
            ColumnInfo(name="Heure"),
            ColumnInfo(name="Type"),
            ColumnInfo(name="Message"),
        ]
        self.table.set_columns(columns)

        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)

        self.table.setEditTriggers(TableWidget.NoEditTriggers)

        self.table.clicked.connect(self.on_click_row)

    def add_row(self, level: LogLevel, msg: str):
        type_text = QStandardItem(level.name)
        msg_text = QStandardItem(msg)
        time_text = QStandardItem(datetime.now().strftime("%H:%M:%S.%f"))

        self.table.item_model.append_row([time_text, type_text, msg_text])

    @pyqtSlot(QModelIndex)
    def on_click_row(self, model_index: QModelIndex):
        source_index = self.table.proxy_model.mapToSource(model_index)
        model = self.table.item_model
        time_text = model.data(model.index(source_index.row(), 0), Qt.DisplayRole)
        type_lvl = model.data(model.index(source_index.row(), 1), Qt.DisplayRole)
        msg_text = model.data(model.index(source_index.row(), 2), Qt.DisplayRole)
        dialog = MessageBox(f"Log {type_lvl} à {time_text}", msg_text, self)
        dialog.exec()
