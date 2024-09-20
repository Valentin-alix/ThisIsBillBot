from PyQt5 import QtCore
from PyQt5.QtWidgets import QStyledItemDelegate


class AlignDelegate(QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        option.displayAlignment = QtCore.Qt.AlignCenter
