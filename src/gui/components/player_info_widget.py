from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from qfluentwidgets import BodyLabel

from src.signals.player_signals import StatePropertySignals


class PlayerInfoWidget(QWidget):
    def __init__(self, player_property_signals: StatePropertySignals):
        super().__init__()
        self.player_property_signals = player_property_signals
        self.setLayout(QVBoxLayout())
        self.properties: dict[str, BodyLabel] = {}
        self.player_property_signals.property_set_by_class.connect(
            self.on_received_property
        )

    @pyqtSlot(str, str)
    def on_received_property(self, key: str, value: str):
        label_value = self.properties.get(key)
        if label_value is not None:
            label_value.setText(value)
        else:
            row = QWidget()
            row.setLayout(QHBoxLayout())
            label_header = BodyLabel(text=key)
            row.layout().addWidget(label_header)
            label_value = BodyLabel(text=value)
            row.layout().addWidget(label_value)
            self.layout().addWidget(row)
            self.properties[key] = label_value
