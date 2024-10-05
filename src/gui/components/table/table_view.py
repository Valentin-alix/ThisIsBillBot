from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtWidgets import QHeaderView, QTableView, QAbstractItemView
from qfluentwidgets import TableView, SmoothMode

from src.gui.components.table.column_info import ColumnInfo
from src.gui.components.table.filter_header_view import FilterHeaderView
from src.gui.components.table.multi_filter_proxy import MultiColumnFilterProxyModel


class CustomTableView(TableView):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.columns_infos: list[ColumnInfo] = []
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)

        self.setSelectionBehavior(QTableView.SelectRows)
        self.setSelectionMode(QTableView.SingleSelection)
        self.scrollDelagate.verticalSmoothScroll.setSmoothMode(SmoothMode.NO_SMOOTH)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.header = FilterHeaderView(Qt.Horizontal, self)
        self.setHorizontalHeader(self.header)
        self.verticalHeader().hide()

        self.item_model = QStandardItemModel()
        self.proxy_model = MultiColumnFilterProxyModel()
        self.proxy_model.setSourceModel(self.item_model)

        self.setModel(self.proxy_model)
        self.model().rowsInserted.connect(self.on_cell_changed)

        self.header.signals.new_filter_input.connect(self.filter_rows)

    def set_columns(self, columns_infos: list[ColumnInfo]) -> None:
        self.item_model.setColumnCount(len(columns_infos))
        self.proxy_model.set_columns(columns_infos)
        self.header.set_columns(columns_infos)
        self.columns_infos = columns_infos

    def filter_rows(self, header_filters: list[str]) -> None:
        self.proxy_model.set_filters(header_filters)

    @pyqtSlot()
    def on_cell_changed(self):
        if self.verticalScrollBar().value() == self.verticalScrollBar().maximum():
            self.scrollToBottom()
