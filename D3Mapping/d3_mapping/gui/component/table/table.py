from qfluentwidgets import SingleDirectionScrollArea

from d3_mapping.gui.component.table.column_info import ColumnInfo
from d3_mapping.gui.component.table.table_view import CustomTableView


class BaseTableWidget(SingleDirectionScrollArea):  # type: ignore
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.columns_infos: list[ColumnInfo] = []
        self.table = CustomTableView(parent=self)

        self.enableTransparentBackground()
        self.setWidget(self.table)
        self.setWidgetResizable(True)
