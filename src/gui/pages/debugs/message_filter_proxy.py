import json

from PyQt6.QtCore import QModelIndex, Qt

from src.gui.components.table.multi_filter_proxy import MultiColumnFilterProxyModel
from src.gui.components.table.column_info import SearchType


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
            text: str = source_index.data()

            if text == "":
                user_data = source_index.data(Qt.ItemDataRole.UserRole)
                if (
                    user_data
                    and hasattr(user_data, "msg_json")
                    and hasattr(user_data, "obf_msg_json")
                ):
                    text = json.dumps(user_data.msg_json) + json.dumps(
                        user_data.obf_msg_json
                    )

            if filter_info.search_type == SearchType.CONTAINS:
                if filter_string.lower() not in text.lower():
                    return False
            if filter_info.search_type == SearchType.EXACT:
                if not filter_string == text:
                    return False
        return True
