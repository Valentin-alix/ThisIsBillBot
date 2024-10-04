from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from qfluentwidgets import LineEdit, BodyLabel

from src.gui.components.table.column_info import ColumnInfo


class HeaderFilterSignals(QObject):
    new_filter_input = pyqtSignal(list)


class HeaderTableItem(QWidget):
    def __init__(self, column_info: ColumnInfo):
        super().__init__()
        self.setLayout(QVBoxLayout())
        title = BodyLabel(column_info.name, self)
        self.layout().addWidget(title)
        if column_info.search_type:
            self.col_search_edit = LineEdit()
            self.layout().addWidget(self.col_search_edit)
        else:
            self.col_search_edit = None


class HeaderTable(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.signals = HeaderFilterSignals()
        self.col_header_edit: list[LineEdit | None] = []
        self.columns_infos: list[ColumnInfo] = []

    def set_columns(self, columns_infos: list[ColumnInfo]) -> None:
        self.columns_infos = columns_infos
        self.setLayout(QHBoxLayout())
        for column_info in columns_infos:
            if column_info.is_hidden:
                self.col_header_edit.append(None)
                continue
            header_item = HeaderTableItem(column_info)
            self.col_header_edit.append(header_item.col_search_edit)
            if header_item.col_search_edit:
                header_item.col_search_edit.textChanged.connect(
                    self.on_new_filter_input
                )
            self.layout().addWidget(header_item)

    @pyqtSlot()
    def on_new_filter_input(self) -> None:
        header_filters = self.get_header_filters()
        self.signals.new_filter_input.emit(header_filters)

    def get_header_filters(self) -> list[str]:
        cols_filters: list[str] = []

        for index, col_info in enumerate(self.columns_infos):
            if not col_info.search_type or col_info.is_hidden:
                cols_filters.append("")
                continue
            col_edit = self.col_header_edit[index]
            assert col_edit is not None
            cols_filters.append(col_edit.text())

        return cols_filters
