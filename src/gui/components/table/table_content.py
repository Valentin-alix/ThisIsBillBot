from typing import cast

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWidget, QHeaderView
from qfluentwidgets import SingleDirectionScrollArea, TableWidget, SmoothMode

from src.gui.components.table.column_info import ColumnInfo, SearchType


class BaseTableContent(SingleDirectionScrollArea):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.columns_infos: list[ColumnInfo] = []
        self.table = TableWidget(parent=self)
        self.table.scrollDelagate.verticalSmoothScroll.setSmoothMode(
            SmoothMode.NO_SMOOTH
        )

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().hide()
        self.table.verticalHeader().hide()

        self.enableTransparentBackground()
        self.setWidget(self.table)
        self.setWidgetResizable(True)

        self.table.cellChanged.connect(self.on_cell_changed)

    def set_columns(self, columns_infos: list[ColumnInfo]) -> None:
        self.columns_infos = columns_infos
        self.table.setColumnCount(len(columns_infos))
        for index, col_info in enumerate(columns_infos):
            self.table.setColumnHidden(index, col_info.is_hidden)

    def filter_row(self, row_index: int, cols_filters: list[str]) -> None:
        for col_index, col_info in enumerate(self.columns_infos):
            if not col_info.search_type or cols_filters[col_index] == "":
                continue

            if col_info.get_texts_func is not None:
                col_widget = self.table.cellWidget(row_index, col_index)
                col_widget = cast(QWidget, col_widget)
                cell_texts = col_info.get_texts_func(col_widget)
            else:
                wid_item = self.table.item(row_index, col_index)
                if not wid_item:
                    continue
                cell_texts = [wid_item.text()]

            if col_info.search_type == SearchType.CONTAINS:
                if all(
                    not cell_text.lower().startswith(cols_filters[col_index].lower())
                    for cell_text in cell_texts
                ):
                    self.table.setRowHidden(row_index, True)
                    break
            elif col_info.search_type == SearchType.EXACT:
                if all(
                    not cell_text == cols_filters[col_index] for cell_text in cell_texts
                ):
                    self.table.setRowHidden(row_index, True)
                    break
        else:
            self.table.setRowHidden(row_index, False)

    def filter_rows(self, header_filters: list[str]) -> None:
        for row_index in range(self.table.rowCount()):
            self.filter_row(row_index, header_filters)

    @pyqtSlot()
    def on_cell_changed(self):
        if (
            self.table.verticalScrollBar().value()
            == self.table.verticalScrollBar().maximum()
        ):
            self.table.scrollToBottom()
