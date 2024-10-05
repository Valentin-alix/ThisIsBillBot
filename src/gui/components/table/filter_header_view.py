import sys
from functools import partial

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt, QObject, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QTableView,
    QHeaderView,
    QVBoxLayout,
    QWidget,
    QAbstractItemView,
)
from qfluentwidgets import LineEdit

from src.gui.components.table.column_info import ColumnInfo


class HeaderFilterSignals(QObject):
    new_filter_input = pyqtSignal(list)


class FilterHeaderView(QHeaderView):
    def __init__(self, orientation: QtCore.Qt.Orientation, parent: QTableView) -> None:
        super().__init__(orientation, parent)
        self.setSectionsClickable(True)
        self.signals = HeaderFilterSignals()
        self.line_edits: list[LineEdit] = []
        self.header_filters: list[str] = []
        self.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.setDefaultAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.sectionResized.connect(self.adjust_positions)
        parent.horizontalScrollBar().valueChanged.connect(self.adjust_positions)

    @pyqtSlot(int, str)
    def on_new_filter_input(self, index: int, value: str) -> None:
        self.header_filters[index] = value
        self.signals.new_filter_input.emit(self.header_filters)

    def set_columns(self, column_infos: list[ColumnInfo]):
        for index, col_info in enumerate(column_infos):
            self.header_filters.append("")
            if col_info.search_type is not None:
                line_edit = LineEdit(self)
                line_edit.setPlaceholderText(col_info.name)
                line_edit.textChanged.connect(partial(self.on_new_filter_input, index))
                self.line_edits.append(line_edit)
            self.setSectionResizeMode(index, QHeaderView.Stretch)
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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Custom Header with QLineEdit")

        col_infos: list[ColumnInfo] = [
            ColumnInfo(name="helloo"),
            ColumnInfo("ici"),
            ColumnInfo(name="etLAAA", search_type=None),
        ]
        # Crée une QTableView
        self.table_view = QTableView(self)
        self.model = QStandardItemModel(10, 3)
        self.model.setHorizontalHeaderLabels(["Column 1", "Column 2", "Column 3"])

        # Remplir le modèle avec des données d'exemple
        for row in range(10):
            for column in range(3):
                item = QStandardItem(f"Item {row}, {column}")
                self.model.setItem(row, column, item)

        self.table_view.setModel(self.model)
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectRows)

        # Crée un en-tête personnalisé et remplace l'en-tête par défaut
        header = FilterHeaderView(Qt.Horizontal, self.table_view)
        self.table_view.setHorizontalHeader(header)
        header.set_columns(col_infos)

        # Ajoute la table dans la fenêtre principale
        layout = QVBoxLayout()
        layout.addWidget(self.table_view)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
