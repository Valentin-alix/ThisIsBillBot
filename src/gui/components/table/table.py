from qfluentwidgets import SingleDirectionScrollArea

from src.gui.components.table.column_info import ColumnInfo
from src.gui.components.table.table_view import CustomTableView


class BaseTableWidget(SingleDirectionScrollArea):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.columns_infos: list[ColumnInfo] = []
        self.table = CustomTableView(parent=self)

        self.enableTransparentBackground()
        self.setWidget(self.table)
        self.setWidgetResizable(True)
