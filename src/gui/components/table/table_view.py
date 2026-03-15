from PyQt6.QtCore import (
    QAbstractTableModel,
    QModelIndex,
    QObject,
    Qt,
    pyqtSignal,
    pyqtSlot,
)
from PyQt6.QtGui import QBrush, QResizeEvent, QStandardItem
from PyQt6.QtWidgets import QAbstractItemView
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
        parent: QObject | None = None,
        max_row_count: int = 5000,
    ) -> None:
        super().__init__(parent)
        self.signals = CustomTableModelSignal(parent=self)
        self._data = data if data is not None else []
        self._column_count = column_count
        self._max_row_count = max_row_count

    def rowCount(self, parent: QModelIndex | None = None) -> int:
        return len(self._data)

    def columnCount(self, parent: QModelIndex | None = None) -> int:
        return self._column_count

    def data(self, index: QModelIndex, role: int | None = None) -> str | QBrush | object | None:
        if not index.isValid():
            return None

        item = self._data[index.row()][index.column()]
        if role == Qt.ItemDataRole.DisplayRole:
            return item.text()
        elif role == Qt.ItemDataRole.UserRole:
            return item.data(Qt.ItemDataRole.UserRole)
        elif role == Qt.ItemDataRole.BackgroundRole:
            color = item.data(Qt.ItemDataRole.BackgroundRole)
            if color is not None:
                return QBrush(color)

        return None

    def set_column_count(self, count: int) -> None:
        self._column_count = count
        self.layoutChanged.emit()

    def append_row(self, row_data: list[QStandardItem]) -> None:
        row_index = len(self._data)
        self.beginInsertRows(QModelIndex(), row_index, row_index)
        self._data.append(row_data)
        self.endInsertRows()

        if len(self._data) > self._max_row_count:
            self.signals.max_row_reached.emit()

    def append_rows(self, rows: list[list[QStandardItem]]) -> None:
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

    def remove_rows(self, row: int, count: int) -> None:
        self.beginRemoveRows(QModelIndex(), row, row + count - 1)
        del self._data[row : row + count]
        self.endRemoveRows()

    def clear_all(self) -> None:
        if self._data:
            self.remove_rows(0, len(self._data))

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled

    def setData(self, index: QModelIndex, value: str, role: int = Qt.ItemDataRole.EditRole) -> bool:
        if not index.isValid():
            return False

        item = self._data[index.row()][index.column()]
        if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
            item.setText(value)
            self.dataChanged.emit(index, index, [role])
            return True
        return False

    def update_row_cells(self, row: int, col_start: int, col_end: int, values: list[str]) -> None:
        if row < 0 or row >= len(self._data):
            return
        for i, value in enumerate(values):
            col = col_start + i
            if col <= col_end and col < self._column_count:
                self._data[row][col].setText(value)
        self.dataChanged.emit(
            self.index(row, col_start),
            self.index(row, col_end),
            [Qt.ItemDataRole.DisplayRole],
        )


class CustomTableView(TableView):
    def __init__(
        self,
        parent: SingleDirectionScrollArea,
        proxy_model: MultiColumnFilterProxyModel | None = None,
        item_model: CustomTableModel | None = None,
    ) -> None:
        super().__init__(parent=parent)
        self.scroll_bar = parent
        self.columns_infos: list[ColumnInfo] = []
        self.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.scrollDelagate.verticalSmoothScroll.setSmoothMode(SmoothMode.NO_SMOOTH)
        self.scrollDelagate.horizonSmoothScroll.setSmoothMode(SmoothMode.NO_SMOOTH)
        self.scrollDelagate.vScrollBar.setScrollAnimation(0)
        self.scrollDelagate.hScrollBar.setScrollAnimation(0)

        self.setWordWrap(False)
        self.setAlternatingRowColors(False)

        self.header = FilterHeaderView(Qt.Orientation.Horizontal, self)
        self.setHorizontalHeader(self.header)
        vertical_header = self.verticalHeader()
        assert vertical_header is not None
        vertical_header.hide()

        self.item_model = item_model or CustomTableModel(parent=self)
        self.item_model.signals.max_row_reached.connect(profiled_slot(self.on_max_row_reached))
        self.proxy_model = proxy_model or MultiColumnFilterProxyModel()
        self.proxy_model.setSourceModel(self.item_model)

        self.setModel(self.proxy_model)
        proxy_model_set = self.model()
        assert proxy_model_set is not None
        proxy_model_set.rowsInserted.connect(profiled_slot(self.keep_scroll_position))
        self.header.signals.new_filter_input.connect(self.filter_rows)

    @pyqtSlot()
    def on_max_row_reached(self):
        scroll_bar = self.scroll_bar.verticalScrollBar()
        assert scroll_bar is not None
        old_scroll_position = scroll_bar.value()
        overflow = self.item_model.rowCount() - self.item_model._max_row_count
        self.item_model.remove_rows(0, min(self.item_model.rowCount(), max(500, overflow)))
        scroll_bar.setValue(old_scroll_position)

    def resizeEvent(self, e: QResizeEvent | None) -> None:
        self.setUpdatesEnabled(False)
        super().resizeEvent(e)
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

    def append_row(self, row: list[QStandardItem]) -> None:
        model = self.item_model
        model.append_row(row)

    def keep_scroll_position(self) -> None:
        vsb = self.verticalScrollBar()
        assert vsb is not None
        if vsb.value() == vsb.maximum():
            self.scrollToBottom()
