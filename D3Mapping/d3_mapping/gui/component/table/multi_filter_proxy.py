from PyQt5.QtCore import QSortFilterProxyModel, QModelIndex

from d3_mapping.gui.component.table.column_info import FilterInfo, SearchType


class MultiColumnFilterProxyModel(QSortFilterProxyModel):
    def __init__(self) -> None:
        super().__init__()
        self.filter_infos: list[FilterInfo | None] = []
        self.header_filters: list[str] = []

    def set_filter_infos(self, filter_infos: list[FilterInfo | None]):
        self.filter_infos.clear()
        for filter_info in filter_infos:
            self.add_filter_info(filter_info)

    def add_filter_info(self, filter_info: FilterInfo | None):
        self.filter_infos.append(filter_info)

    def set_filters(self, header_filters: list[str]) -> None:
        self.header_filters = header_filters
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex):
        for col_index, filter_string in enumerate(self.header_filters):
            filter_info = self.filter_infos[col_index]
            if not filter_info:
                continue
            text: str = (
                self.sourceModel().index(source_row, col_index, source_parent).data()
            )
            if filter_info.search_type == SearchType.CONTAINS:
                if filter_string.lower() not in text.lower():
                    return False
            if filter_info.search_type == SearchType.EXACT:
                if not filter_string == text:
                    return False
        return True
