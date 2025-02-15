from datetime import datetime

from PyQt6.QtCore import QModelIndex, Qt, pyqtSlot
from PyQt6.QtGui import QStandardItem
from PyQt6.QtWidgets import QHeaderView
from qfluentwidgets import TableWidget

from src.gui.components.qfluent_widget.scrollable_message_box import (
    ScrollableMessageBox,
)
from PyQt6.QtWidgets import QWidget

from src.gui.components.table.column_info import ColumnInfo
from src.gui.components.table.table import BaseTableWidget
from src.services.logging.log_level import LogLevel


def _require_display_text(value: object) -> str:
    if not isinstance(value, str):
        raise TypeError("Expected a string display value in the logs table model")
    return value


class LogsTable(BaseTableWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        columns: list[ColumnInfo] = [
            ColumnInfo(name="Heure"),
            ColumnInfo(name="Type"),
            ColumnInfo(name="Message"),
        ]
        self.table.set_columns(columns)

        header = self.table.horizontalHeader()
        assert header is not None
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)

        self.table.setColumnWidth(0, 100)
        self.table.setColumnWidth(1, 100)

        self.table.setEditTriggers(TableWidget.EditTrigger.NoEditTriggers)

        self.table.clicked.connect(self.on_click_row)

    def add_row(self, level: LogLevel, msg: str) -> None:
        type_text = QStandardItem(level.name)
        msg_text = QStandardItem(msg)
        logged_at = datetime.now()
        time_text = QStandardItem(logged_at.strftime("%H:%M:%S"))
        time_text.setData(logged_at, Qt.ItemDataRole.UserRole)

        # use buffered append to insert logs in batches
        self.table.append_row([time_text, type_text, msg_text])

    @pyqtSlot(QModelIndex)
    def on_click_row(self, model_index: QModelIndex) -> None:
        source_index = self.table.proxy_model.mapToSource(model_index)
        model = self.table.item_model
        time_text = model.data(
            model.index(source_index.row(), 0), Qt.ItemDataRole.DisplayRole
        )
        type_lvl = model.data(
            model.index(source_index.row(), 1), Qt.ItemDataRole.DisplayRole
        )
        msg_text = _require_display_text(
            model.data(model.index(source_index.row(), 2), Qt.ItemDataRole.DisplayRole)
        )
        dialog = ScrollableMessageBox(f"Log {type_lvl} à {time_text}", msg_text, self)
        dialog.exec()
