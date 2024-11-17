from typing import Any, Callable

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeyEvent, QKeySequence
from PyQt5.QtWidgets import QApplication, QMenu, QTreeWidgetItem
from qfluentwidgets import TreeWidget


class DynamicTreeWidget(TreeWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.header().hide()
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

    def _copy_selected_text(self):
        item = self.currentItem()
        if item is None:
            return
        QApplication.clipboard().setText(item.text(0))

    def _show_context_menu(self, pos):
        item = self.itemAt(pos)
        if item is None:
            return
        menu = QMenu(self)
        copy_action = menu.addAction("Copier")
        if menu.exec_(self.viewport().mapToGlobal(pos)) == copy_action:
            QApplication.clipboard().setText(item.text(0))

    def keyPressEvent(self, event: QKeyEvent):
        if event.matches(QKeySequence.Copy):
            self._copy_selected_text()
        else:
            super().keyPressEvent(event)

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
