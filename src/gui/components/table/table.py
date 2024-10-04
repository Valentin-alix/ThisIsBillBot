from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
)

from src.gui.components.table.column_info import ColumnInfo
from src.gui.components.table.header_table import HeaderTable
from src.gui.components.table.table_content import BaseTableContent


class BaseTableWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setLayout(QVBoxLayout())
        self.columns_infos: list[ColumnInfo] = []

        self.header = HeaderTable()
        self.table_content = BaseTableContent()
        self.table_content.table.cellChanged.connect(self.on_cell_changed)

        self.header.signals.new_filter_input.connect(self.table_content.filter_rows)

        self.layout().addWidget(self.header)
        self.layout().addWidget(self.table_content)

    def set_columns(self, columns_infos: list[ColumnInfo]):
        self.columns_infos = columns_infos
        self.header.set_columns(columns_infos)
        self.table_content.set_columns(columns_infos)

    @pyqtSlot(int, int)
    def on_cell_changed(self, row_index: int, _: int):
        cols_filters = self.header.get_header_filters()
        self.table_content.filter_row(row_index, cols_filters)
