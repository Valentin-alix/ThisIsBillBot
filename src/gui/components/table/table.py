from qfluentwidgets import SingleDirectionScrollArea

from src.gui.components.table.column_info import ColumnInfo
from src.gui.components.table.multi_filter_proxy import MultiColumnFilterProxyModel
from src.gui.components.table.table_view import CustomTableView


class BaseTableWidget(SingleDirectionScrollArea):
    def __init__(
        self, proxy_model: MultiColumnFilterProxyModel | None = None, *args, **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)

        self.columns_infos: list[ColumnInfo] = []
        self.table = CustomTableView(parent=self, proxy_model=proxy_model)

        self.enableTransparentBackground()
        self.setWidget(self.table)
        self.setWidgetResizable(True)
