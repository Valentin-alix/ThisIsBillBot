from PyQt6.QtWidgets import QWidget

from src.gui.components.group_box import GroupBox
from src.gui.pages.farmer.player_info.property_widget import PropertyWidget


class PropertyGroupWidget(GroupBox):
    def __init__(self, key: str, vertical: bool = False, parent: QWidget | None = None):
        super().__init__(key, parent=parent)
        self._vertical = vertical
        self.property_by_key: dict[str, PropertyWidget] = {}

    def add_or_update_property_label(self, key: str, value: str) -> None:
        property_widget: PropertyWidget | None = self.property_by_key.get(key)
        if property_widget is not None:
            property_widget.set_content_value(value)
        else:
            property_widget = PropertyWidget(key=key, value=value, vertical=self._vertical)
            self.add_widget(property_widget)
            self.property_by_key[key] = property_widget
