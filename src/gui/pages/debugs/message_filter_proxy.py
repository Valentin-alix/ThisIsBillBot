import json

from PyQt5.QtCore import QModelIndex, Qt

from src.gui.components.table.multi_filter_proxy import MultiColumnFilterProxyModel
from src.gui.components.table.column_info import SearchType


class MessageFilterProxyModel(MultiColumnFilterProxyModel):
    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex):
        for col_index, filter_string in enumerate(self.header_filters):
            filter_info = self.filter_infos[col_index]
            if not filter_info:
                continue

            source_index = self.sourceModel().index(source_row, col_index, source_parent)
            text: str = source_index.data()

            if text == "":
                user_data = source_index.data(Qt.UserRole)
                if user_data and hasattr(user_data, 'msg_json') and hasattr(user_data, 'obf_msg_json'):
                    text = json.dumps(user_data.msg_json) + json.dumps(user_data.obf_msg_json)

            if filter_info.search_type == SearchType.CONTAINS:
                if filter_string.lower() not in text.lower():
                    return False
            if filter_info.search_type == SearchType.EXACT:
                if not filter_string == text:
                    return False
        return True
