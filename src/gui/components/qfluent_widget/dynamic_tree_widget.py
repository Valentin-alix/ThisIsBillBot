from typing import Callable, TypeAlias

from PyQt6.QtCore import QPoint, Qt
from PyQt6.QtGui import QKeyEvent, QKeySequence
from PyQt6.QtWidgets import QApplication, QMenu, QTreeWidgetItem, QWidget
from qfluentwidgets import TreeWidget

TreeValue: TypeAlias = (
    str | int | float | bool | None | dict[str, "TreeValue"] | list["TreeValue"]
)


class DynamicTreeWidget(TreeWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        header = self.header()
        assert header is not None
        header.hide()
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

    def _copy_selected_text(self) -> None:
        item = self.currentItem()
        if item is None:
            return
        clipboard = QApplication.clipboard()
        assert clipboard is not None
        clipboard.setText(item.text(0))

    def _show_context_menu(self, pos: QPoint) -> None:
        item = self.itemAt(pos)
        if item is None:
            return
        menu = QMenu(self)
        copy_action = menu.addAction("Copier")
        viewport = self.viewport()
        assert viewport is not None
        if menu.exec(viewport.mapToGlobal(pos)) == copy_action:
            clipboard = QApplication.clipboard()
            assert clipboard is not None
            clipboard.setText(item.text(0))

    def keyPressEvent(self, event: QKeyEvent | None) -> None:
        if event is not None and event.matches(QKeySequence.StandardKey.Copy):
            self._copy_selected_text()
        else:
            super().keyPressEvent(event)

    def set_content(
        self,
        datas: dict[str, TreeValue],
        get_display_value: Callable[[TreeValue], str | None] | None = None,
    ) -> None:
        self.setUpdatesEnabled(False)
        self.clear()
        self._deep_tree_from_message_dict(datas, get_display_value, None, self)
        self.expandToDepth(1)
        self.setUpdatesEnabled(True)

    def _deep_tree_from_message_dict(
        self,
        values: TreeValue,
        get_display_value: Callable[[TreeValue], str | None] | None,
        parent: QTreeWidgetItem | None = None,
        base_qtree: TreeWidget | None = None,
    ) -> None:
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
                            {str(index): _value}, get_display_value, widget_item
                        )
                else:
                    widget_item = QTreeWidgetItem([f"{key} = {value}"])
                if parent is not None:
                    parent.addChild(widget_item)
                elif base_qtree is not None:
                    base_qtree.addTopLevelItem(widget_item)
