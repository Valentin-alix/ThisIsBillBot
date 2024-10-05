from typing import Any

from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import QVBoxLayout, QWidget

from src.gui.components.player_info.property_group_widget import PropertyGroupWidget
from src.signals.player_signals import StatePropertySignals


class PlayerInfoWidget(QWidget):
    def __init__(self, player_property_signals: StatePropertySignals):
        super().__init__()
        v_layout = QVBoxLayout()
        v_layout.setAlignment(Qt.AlignTop)
        self.setLayout(v_layout)

        self.player_property_signals = player_property_signals
        self.group_by_key: dict[str, PropertyGroupWidget] = {}
        self.player_property_signals.property_set_by_class.connect(
            self.on_received_property
        )

    @pyqtSlot(str, str, str)
    def on_received_property(self, group_key: str, key: str, value: Any):
        group_widget = self.get_or_create_group_widget(group_key)
        group_widget.add_or_update_property_label(key, value)

    def get_or_create_group_widget(self, group_key: str) -> PropertyGroupWidget:
        group_widget = self.group_by_key.get(group_key)
        if group_widget is not None:
            return group_widget

        group_widget = PropertyGroupWidget(key=group_key)
        self.group_by_key[group_key] = group_widget
        self.layout().addWidget(group_widget)

        return group_widget
