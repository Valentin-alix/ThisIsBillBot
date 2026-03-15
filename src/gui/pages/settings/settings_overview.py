from functools import partial

from PyQt6.QtCore import QSignalBlocker, Qt, pyqtSignal
from PyQt6.QtWidgets import QHeaderView, QSizePolicy, QTableWidgetItem, QVBoxLayout, QWidget
from qfluentwidgets import BodyLabel, FluentIcon, PushButton, TableWidget, TransparentToolButton, SmoothMode


class SettingsOverview(QWidget):
    selected = pyqtSignal()
    delete_requested = pyqtSignal(str)

    def __init__(self, headers: list[str], parent: QWidget, new_label: str | None = None) -> None:
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.keys: list[str] = []
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 16)
        self.count = BodyLabel("", self)
        layout.addWidget(self.count)
        self.table = TableWidget(self)
        self.table.setColumnCount(len(headers) + 1)
        self.table.setHorizontalHeaderLabels([*headers, ""])
        self.table.scrollDelagate.verticalSmoothScroll.setSmoothMode(SmoothMode.NO_SMOOTH)
        self.table.scrollDelagate.horizonSmoothScroll.setSmoothMode(SmoothMode.NO_SMOOTH)
        self.table.scrollDelagate.vScrollBar.setScrollAnimation(0)
        self.table.scrollDelagate.hScrollBar.setScrollAnimation(0)
        self.table.setEditTriggers(TableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(TableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(TableWidget.SelectionMode.SingleSelection)
        vertical = self.table.verticalHeader()
        horizontal = self.table.horizontalHeader()
        assert vertical is not None and horizontal is not None
        vertical.hide()
        horizontal.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        horizontal.setStretchLastSection(False)
        horizontal.setSectionResizeMode(len(headers) - 1, QHeaderView.ResizeMode.Stretch)
        horizontal.setSectionResizeMode(len(headers), QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(len(headers), 36)
        layout.addWidget(self.table)
        self.empty = BodyLabel("No saved items.", self)
        layout.addWidget(self.empty)
        self.new_button = PushButton(new_label or "New…", self)
        self.new_button.setVisible(new_label is not None)
        layout.addWidget(self.new_button, alignment=Qt.AlignmentFlag.AlignLeft)
        self.new_button.clicked.connect(lambda: self.select_key(None))
        self.table.itemSelectionChanged.connect(self.selected.emit)

    @property
    def selected_key(self) -> str | None:
        selection = self.table.selectionModel()
        assert selection is not None
        rows = selection.selectedRows()
        return self.keys[rows[0].row()] if rows else None

    def select_key(self, key: str | None) -> None:
        with QSignalBlocker(self.table):
            self.table.clearSelection()
            if key in self.keys:
                self.table.selectRow(self.keys.index(key))
        self.selected.emit()

    def _request_delete(self, key: str, _checked: bool = False) -> None:
        self.delete_requested.emit(key)

    def set_rows(self, rows: list[tuple[str, tuple[str, ...]]]) -> None:
        selected = self.selected_key
        with QSignalBlocker(self.table):
            self.table.clearSelection()
            self.keys = [key for key, _ in rows]
            self.table.setRowCount(len(rows))
            for row, (key, values) in enumerate(rows):
                for column, value in enumerate(values):
                    item = QTableWidgetItem(value)
                    item.setToolTip(value)
                    self.table.setItem(row, column, item)
                line_count = max(value.count("\n") + 1 for value in values)
                self.table.setRowHeight(row, max(32, self.table.fontMetrics().lineSpacing() * line_count + 12))
                button = TransparentToolButton(FluentIcon.CLOSE, self.table)
                button.setToolTip("Delete")
                button.setAccessibleName(f"Delete {key}")
                button.clicked.connect(partial(self._request_delete, key))
                self.table.setCellWidget(row, len(values), button)
            self.table.setFixedHeight(min(240, 40 + sum(self.table.rowHeight(i) for i in range(len(rows)))))
            if selected in self.keys:
                self.table.selectRow(self.keys.index(selected))
        self.count.setText(f"{len(rows)} saved item(s)")
        self.empty.setVisible(not rows)
        self.table.setVisible(bool(rows))
