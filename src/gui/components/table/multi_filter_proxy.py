from PyQt5.QtCore import QSortFilterProxyModel, QModelIndex

from src.gui.components.table.column_info import ColumnInfo, SearchType


class MultiColumnFilterProxyModel(QSortFilterProxyModel):
    def __init__(self) -> None:
        super().__init__()
        self.column_infos: list[ColumnInfo] = []
        self.header_filters: list[str] = []

    def set_columns(self, column_infos: list[ColumnInfo]):
        self.column_infos = column_infos

    def set_filters(self, header_filters: list[str]) -> None:
        self.header_filters = header_filters
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex):
        for col_index, filter_string in enumerate(self.header_filters):
            col_info = self.column_infos[col_index]
            text: str = (
                self.sourceModel().index(source_row, col_index, source_parent).data()
            )
            if col_info.search_type == SearchType.CONTAINS:
                if filter_string.lower() not in text.lower():
                    return False
            if col_info.search_type == SearchType.EXACT:
                if not filter_string == text:
                    return False
        return True
