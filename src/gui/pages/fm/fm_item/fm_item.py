from logging import Logger

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QFormLayout, QLineEdit, QVBoxLayout, QWidget

from src.core.engine.fms.equipment import EquipmentSchema, LineSchema, StatSchema
from src.gui.pages.fm.fm_item.fm_item_table import FmItemTable


class FmItemSignals(QObject):
    saved_item = pyqtSignal(EquipmentSchema)
    created_item = pyqtSignal(EquipmentSchema)
    deleted_item = pyqtSignal(EquipmentSchema)


class FmItem(QWidget):
    def __init__(
        self,
        logger: Logger,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.logger = logger
        self.signals = FmItemSignals(parent=self)
        self.equipment: EquipmentSchema | None = None

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self._setup_item_content()

    def set_item_from_equipment(self, equipment: EquipmentSchema):
        self.equipment = equipment
        self.fm_item_table.set_table_from_equipment(equipment)

    def set_item_from_base_lines(self, base_lines: list[LineSchema]):
        self.equipment = None
        self.label_edit.setText("")

    def get_exo_stat(self) -> StatSchema | None:
        return
        stat_id: int | None = self.fm_item_table.exo_combo.currentData()
        if stat_id is None:
            return None
        related_stat: StatSchema = next(
            _elem for _elem in self.fm_item_table.stats if _elem.id == stat_id
        )
        return related_stat

    def get_edited_label(self) -> str:
        return self.label_edit.text()

    def get_edited_lines(self) -> list[LineSchema]:
        edited_lines: list[LineSchema] = []
        for line_edit, line_schema in self.fm_item_table.edits_with_line:
            line_schema.value = int(line_edit.text())
            edited_lines.append(line_schema)
        return edited_lines

    def _setup_item_content(self):
        self.label_equip_widget = QWidget(self)
        self.label_equip_layout = QFormLayout()
        self.label_equip_widget.setLayout(self.label_equip_layout)
        self.label_edit = QLineEdit(self.label_equip_widget)
        self.label_equip_layout.addRow("Label", self.label_edit)
        self.main_layout.addWidget(self.label_equip_widget)

        self.fm_item_table: FmItemTable = FmItemTable(self)
        self.main_layout.addWidget(self.fm_item_table)
