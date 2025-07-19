from typing import Any

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QVBoxLayout, QWidget
from qfluentwidgets import SingleDirectionScrollArea

from src.gui.pages.farmer.player_info.property_group_widget import PropertyGroupWidget


class PropertyPanelWidget(QWidget):
    """Generic scrollable panel that displays grouped key/value properties.

    Properties are pushed via ``on_received_property`` (typically connected to
    signals through ``functools.partial``) and flushed in batch on the event loop.
    """

    def __init__(self, vertical: bool = False, parent: QWidget | None = None):
        super().__init__(parent=parent)
        self._vertical = vertical

        scroll_area = SingleDirectionScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        container_widget = QWidget(scroll_area)
        self.container_layout = QVBoxLayout()
        self.container_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        container_widget.setLayout(self.container_layout)

        scroll_area.setWidget(container_widget)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)

        self.group_by_key: dict[str, PropertyGroupWidget] = {}
        self._pending_updates: dict[tuple[str, str], Any] = {}
        self._update_scheduled = False

    def on_received_property(self, group_key: str, key: str, value: Any):
        self._pending_updates[(group_key, key)] = value
        if not self._update_scheduled:
            self._update_scheduled = True
            QTimer.singleShot(0, self._flush_updates)

    def _flush_updates(self):
        for (group_key, key), value in self._pending_updates.items():
            group_widget = self.get_or_create_group_widget(group_key)
            group_widget.add_or_update_property_label(key, str(value))
        self._pending_updates.clear()
        self._update_scheduled = False

    def get_or_create_group_widget(self, group_key: str) -> PropertyGroupWidget:
        group_widget = self.group_by_key.get(group_key)
        if group_widget is not None:
            return group_widget

        group_widget = PropertyGroupWidget(key=group_key, vertical=self._vertical)
        self.group_by_key[group_key] = group_widget
        self.container_layout.addWidget(group_widget)

        return group_widget

    def pre_create_group(self, group_key: str) -> PropertyGroupWidget:
        """Create the group now so callers can show/hide it before any update."""
        return self.get_or_create_group_widget(group_key)
