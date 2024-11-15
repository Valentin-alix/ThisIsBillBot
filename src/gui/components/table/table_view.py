from PyQt5.QtCore import (
    QAbstractTableModel,
    QModelIndex,
    QObject,
    Qt,
    pyqtSignal,
    pyqtSlot,
)
from PyQt5.QtGui import QBrush, QStandardItem
from PyQt5.QtWidgets import QAbstractItemView
from qfluentwidgets import SingleDirectionScrollArea, SmoothMode, TableView

from src.gui.components.table.column_info import ColumnInfo
from src.gui.components.table.filter_header_view import FilterHeaderView
from src.gui.components.table.multi_filter_proxy import MultiColumnFilterProxyModel
from src.gui.utils.profiling import profiled_slot


class CustomTableModelSignal(QObject):
    max_row_reached = pyqtSignal()
    batched_rows = pyqtSignal()


class CustomTableModel(QAbstractTableModel):
    def __init__(
        self,
        data: list[list[QStandardItem]] | None = None,
        column_count: int = 0,
        parent=None,
        max_row_count: int = 2000,
    ):
        super().__init__(parent)
        self.signals = CustomTableModelSignal()
        self._data = data if data is not None else []
        self._column_count = column_count
        self._max_row_count = max_row_count

    def rowCount(self, parent=None, *args, **kwargs) -> int:
        return len(self._data)

    def columnCount(self, parent=None) -> int:
        return self._column_count

    def data(self, index: QModelIndex, role: int | None = None):
        if not index.isValid():
            return None

        item = self._data[index.row()][index.column()]
        if role == Qt.DisplayRole:
            return item.text()
        elif role == Qt.UserRole:
            return item.data(Qt.UserRole)
        elif role == Qt.BackgroundRole:
            color = item.data(Qt.BackgroundRole)
            if color is not None:
                return QBrush(color)

        return None

    def set_column_count(self, count: int):
        self._column_count = count
        self.layoutChanged.emit()

    def append_row(self, row_data: list[QStandardItem]):
        row_index = len(self._data)
        self.beginInsertRows(QModelIndex(), row_index, row_index)
        self._data.append(row_data)
        self.endInsertRows()

        if len(self._data) > self._max_row_count:
            self.signals.max_row_reached.emit()

    def append_rows(self, rows: list[list[QStandardItem]]):
        if not rows:
            return
        start = len(self._data)
        end = start + len(rows) - 1
        self.beginInsertRows(QModelIndex(), start, end)
        self._data.extend(rows)
        self.endInsertRows()
        self.signals.batched_rows.emit()
        if len(self._data) > self._max_row_count:
            self.signals.max_row_reached.emit()

    def remove_rows(self, row: int, count: int):
        self.beginRemoveRows(QModelIndex(), row, row + count - 1)
        del self._data[row : row + count]
        self.endRemoveRows()

    def clear_all(self):
        self.remove_rows(0, len(self._data))

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid():
            return Qt.NoItemFlags  # type: ignore
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled


class CustomTableView(TableView):  # type: ignore
    def __init__(self, parent: SingleDirectionScrollArea) -> None:
        super().__init__(parent=parent)
        self.scroll_bar = parent
        self.columns_infos: list[ColumnInfo] = []
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.NoSelection)
        self.scrollDelagate.verticalSmoothScroll.setSmoothMode(SmoothMode.NO_SMOOTH)

        # optimization
        self.setWordWrap(False)
        self.setAlternatingRowColors(False)

        self.header = FilterHeaderView(Qt.Horizontal, self)
        self.setHorizontalHeader(self.header)
        self.verticalHeader().hide()

        self.item_model = CustomTableModel(parent=self)
        self.item_model.signals.max_row_reached.connect(
            profiled_slot(self.on_max_row_reached)
        )
        self.proxy_model = MultiColumnFilterProxyModel()
        self.proxy_model.setSourceModel(self.item_model)

        self.setModel(self.proxy_model)
        self.model().rowsInserted.connect(profiled_slot(self.keep_scroll_position))
        self.item_model.signals.batched_rows.connect(
            profiled_slot(self.keep_scroll_position)
        )
        self.header.signals.new_filter_input.connect(self.filter_rows)

    @pyqtSlot()
    def on_max_row_reached(self):
        old_scroll_position = self.scroll_bar.verticalScrollBar().value()
        self.item_model.remove_rows(0, 100)
        self.scroll_bar.verticalScrollBar().setValue(old_scroll_position)

    def resizeEvent(self, event):  # type: ignore
        self.setUpdatesEnabled(False)
        super().resizeEvent(event)
        self.setUpdatesEnabled(True)

    def set_columns(self, columns_infos: list[ColumnInfo]) -> None:
        self.item_model.set_column_count(len(columns_infos))
        self.proxy_model.set_filter_infos([col.filter_info for col in columns_infos])
        self.header.set_columns(columns_infos)
        for index, col_info in enumerate(columns_infos):
            if col_info.is_hidden:
                self.hideColumn(index)
        self.columns_infos = columns_infos

    def filter_rows(self, header_filters: list[str]) -> None:
        self.proxy_model.set_filters(header_filters)

    def append_row(self, row: list[QStandardItem]):
        model = self.item_model
        model.append_row(row)

    def keep_scroll_position(self):
        if self.verticalScrollBar().value() == self.verticalScrollBar().maximum():
            self.scrollToBottom()
