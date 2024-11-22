from PyQt6.QtWidgets import QLabel, QLineEdit

from src.core.engine.fms.equipment import EquipmentSchema, LineSchema, StatSchema
from src.gui.components.table.column_info import ColumnInfo
from src.gui.components.table.table import BaseTableWidget


class FmItemTable(BaseTableWidget):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.labels_spent_by_stat_id: dict[int, tuple[QLabel, QLabel]] = {}
        self.edits_with_line: list[tuple[QLineEdit, LineSchema]] = []
        self.stats = []
        self.sorted_exo_stats: list[StatSchema] = sorted(self.stats)
        self.count_lines_achieved: int | None = None

    def set_table_from_equipment(self, equipment: EquipmentSchema):
        return
        self.clear_table()
        columns = [
            ColumnInfo(name="Stat"),
            ColumnInfo(name="Valeur"),
            ColumnInfo(name="Tentatives"),
            ColumnInfo(name="Tentatives Moyenne"),
        ]
        self.table.set_columns(columns)

        for line in equipment.lines:
            table_index = self.table.rowCount()
            self.table.setRowCount(table_index + 1)
            self.mouseDoubleClickEvent(table_index, line)

        table_index = self.table.rowCount()
        self.table.setRowCount(table_index + 1)
        if equipment.exo_stat:
            self._add_exo_line(
                table_index,
                equipment.exo_stat,
                [_elem.stat for _elem in equipment.lines],
            )
        else:
            self._add_empty_exo_line(
                table_index, [_elem.stat for _elem in equipment.lines]
            )
