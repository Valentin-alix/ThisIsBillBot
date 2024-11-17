from typing import Any, Callable

from PyQt5.QtWidgets import QTreeWidgetItem
from qfluentwidgets import TreeWidget


class DynamicTreeWidget(TreeWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.header().hide()

    def set_content(
        self, datas: dict, get_display_value: Callable[[Any], str] | None = None
    ):
        self.setUpdatesEnabled(False)
        self.clear()
        self._deep_tree_from_message_dict(datas, get_display_value, None, self)
        self.expandToDepth(1)
        self.setUpdatesEnabled(True)

    def _deep_tree_from_message_dict(
        self,
        values: Any,
        get_display_value: Callable[[Any], str | None] | None,
        parent: QTreeWidgetItem | None = None,
        base_qtree: TreeWidget | None = None,
    ):
        if not isinstance(values, dict):
            widget_item = QTreeWidgetItem([f"{values}"])
            if parent is not None:
                parent.addChild(widget_item)
        else:
            for key, value in values.items():
                if get_display_value:
                    display_value = get_display_value(value)
                    if display_value is not None:
                        value = display_value
                if isinstance(value, dict):
                    widget_item = QTreeWidgetItem([f"{key}"])
                    self._deep_tree_from_message_dict(
                        value, get_display_value, widget_item
                    )
                elif isinstance(value, list):
                    widget_item = QTreeWidgetItem([f"{key}"])
                    for index, _value in enumerate(value):
                        self._deep_tree_from_message_dict(
                            {index: _value}, get_display_value, widget_item
                        )
                else:
                    widget_item = QTreeWidgetItem([f"{key} = {value}"])
                if parent is not None:
                    parent.addChild(widget_item)
                elif base_qtree is not None:
                    base_qtree.addTopLevelItem(widget_item)
