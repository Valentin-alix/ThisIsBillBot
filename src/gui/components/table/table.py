from PyQt6.QtWidgets import QWidget
from qfluentwidgets import SingleDirectionScrollArea

from src.gui.components.table.column_info import ColumnInfo
from src.gui.components.table.multi_filter_proxy import MultiColumnFilterProxyModel
from src.gui.components.table.table_view import CustomTableModel, CustomTableView


class BaseTableWidget(SingleDirectionScrollArea):
    def __init__(
        self,
        proxy_model: MultiColumnFilterProxyModel | None = None,
        item_model: CustomTableModel | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self.columns_infos: list[ColumnInfo] = []
        self.table = CustomTableView(parent=self, proxy_model=proxy_model, item_model=item_model)

        self.enableTransparentBackground()
        self.setWidget(self.table)
        self.setWidgetResizable(True)
