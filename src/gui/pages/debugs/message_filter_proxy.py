from PyQt6.QtCore import QModelIndex, Qt

from src.gui.components.table.column_info import SearchType
from src.gui.components.table.multi_filter_proxy import MultiColumnFilterProxyModel


MESSAGE_SEARCH_ROLE = int(Qt.ItemDataRole.UserRole) + 1


class MessageFilterProxyModel(MultiColumnFilterProxyModel):
    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex):
        for col_index, filter_string in enumerate(self.header_filters):
            if not filter_string:
                continue
            filter_info = self.filter_infos[col_index]
            if not filter_info:
                continue

            source_model = self.sourceModel()
            assert source_model is not None
            source_index = source_model.index(source_row, col_index, source_parent)
            text = source_index.data()

            if text == "":
                text = source_index.data(MESSAGE_SEARCH_ROLE)

            if not isinstance(text, str):
                raise TypeError("Expected searchable message text")

            if filter_info.search_type == SearchType.CONTAINS:
                if filter_string.casefold() not in text.casefold():
                    return False
            if filter_info.search_type == SearchType.EXACT:
                if not filter_string == text:
                    return False
        return True
