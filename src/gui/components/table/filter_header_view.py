from functools import partial

from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import QObject, QTimer, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import (
    QHeaderView,
    QTableView,
)
from qfluentwidgets import LineEdit

from src.gui.components.table.column_info import ColumnInfo
from src.gui.utils.profiling import profiled_slot


class HeaderFilterSignals(QObject):
    new_filter_input = pyqtSignal(list)


class FilterHeaderView(QHeaderView):
    def __init__(self, orientation: QtCore.Qt.Orientation, parent: QTableView) -> None:
        super().__init__(orientation, parent)
        self.setSectionsClickable(True)
        self.signals = HeaderFilterSignals(parent=self)
        self.line_edits: list[LineEdit] = []
        self.header_filters: list[str] = []
        self._filter_timer = QTimer(self)
        self._filter_timer.setInterval(250)
        self._filter_timer.setSingleShot(True)
        self._filter_timer.timeout.connect(self._emit_filters)
        self.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.setDefaultAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.sectionResized.connect(profiled_slot(self.adjust_positions))
        hsb = parent.horizontalScrollBar()
        assert hsb is not None
        hsb.valueChanged.connect(profiled_slot(self.adjust_positions))

    @pyqtSlot(int, str)
    def on_new_filter_input(self, index: int, value: str) -> None:
        self.header_filters[index] = value
        self._filter_timer.start()

    def _emit_filters(self) -> None:
        self.signals.new_filter_input.emit(list(self.header_filters))

    def set_columns(self, column_infos: list[ColumnInfo]):
        for index, col_info in enumerate(column_infos):
            self.header_filters.append("")
            if col_info.filter_info is not None:
                line_edit = LineEdit(self)
                line_edit.setPlaceholderText(col_info.name)
                line_edit.textChanged.connect(partial(self.on_new_filter_input, index))
                self.line_edits.append(line_edit)
            self.setSectionResizeMode(index, QHeaderView.ResizeMode.Stretch)
        self.adjust_positions()

    def sizeHint(self):
        size = super().sizeHint()
        if self.line_edits:
            height = self.line_edits[0].sizeHint().height()
            size.setHeight(size.height() + height)
        return size

    def updateGeometries(self):
        if self.line_edits:
            height = self.line_edits[0].sizeHint().height()
            self.setViewportMargins(0, 0, 8, super().sizeHint().height() + height)
        else:
            self.setViewportMargins(0, 0, 0, 0)
        super().updateGeometries()
        self.adjust_positions()

    def adjust_positions(self):
        for index, editor in enumerate(self.line_edits):
            height = editor.sizeHint().height()
            editor.move(
                self.sectionPosition(index) - self.offset(),
                height,
            )
            editor.resize(self.sectionSize(index), height)
