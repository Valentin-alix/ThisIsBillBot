from datetime import datetime

from PyQt6.QtCore import QModelIndex, Qt, QTimer, pyqtSlot
from PyQt6.QtGui import QStandardItem
from PyQt6.QtWidgets import QHeaderView, QWidget
from qfluentwidgets import TableWidget

from src.gui.components.qfluent_widget.scrollable_message_box import (
    ScrollableMessageBox,
)
from src.gui.components.table.column_info import ColumnInfo
from src.gui.components.table.table import BaseTableWidget
from src.services.logging_utils.log_level import LogLevel


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
        self._pending_rows: list[tuple[LogLevel, str, datetime]] = []
        self._batch_timer = QTimer(self)
        self._batch_timer.setInterval(50)
        self._batch_timer.setSingleShot(True)
        self._batch_timer.timeout.connect(self._flush_pending_rows)

    def add_row(self, level: LogLevel, msg: str) -> None:
        self._pending_rows.append((level, msg, datetime.now()))
        if not self._batch_timer.isActive():
            self._batch_timer.start()

    def clear(self) -> None:
        self._batch_timer.stop()
        self._pending_rows.clear()
        self.table.item_model.clear_all()

    def _flush_pending_rows(self) -> None:
        if not self._pending_rows:
            return

        rows: list[list[QStandardItem]] = []
        for level, msg, logged_at in self._pending_rows:
            type_text = QStandardItem(level.name)
            msg_text = QStandardItem(msg)
            time_text = QStandardItem(logged_at.strftime("%H:%M:%S"))
            time_text.setData(logged_at, Qt.ItemDataRole.UserRole)
            rows.append([time_text, type_text, msg_text])

        self.table.item_model.append_rows(rows)
        self._pending_rows.clear()

    @pyqtSlot(QModelIndex)
    def on_click_row(self, model_index: QModelIndex) -> None:
        source_index = self.table.proxy_model.mapToSource(model_index)
        model = self.table.item_model
        time_text = model.data(model.index(source_index.row(), 0), Qt.ItemDataRole.DisplayRole)
        type_lvl = model.data(model.index(source_index.row(), 1), Qt.ItemDataRole.DisplayRole)
        msg_text = _require_display_text(
            model.data(model.index(source_index.row(), 2), Qt.ItemDataRole.DisplayRole)
        )
        dialog = ScrollableMessageBox(f"Log {type_lvl} à {time_text}", msg_text, self)
        dialog.exec()
