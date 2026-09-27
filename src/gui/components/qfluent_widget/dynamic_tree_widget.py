from collections.abc import Callable
from typing import TypeAlias, cast

from PyQt6.QtCore import QPoint, Qt
from PyQt6.QtGui import QKeyEvent, QKeySequence
from PyQt6.QtWidgets import QApplication, QMenu, QTreeWidgetItem, QWidget
from qfluentwidgets import TreeWidget

TreeValue: TypeAlias = str | int | float | bool | None | dict[str, "TreeValue"] | list["TreeValue"]


class DynamicTreeWidget(TreeWidget):
    IS_FIELD_ROLE = Qt.ItemDataRole.UserRole + 2
    FIELD_PATH_ROLE = Qt.ItemDataRole.UserRole + 3

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

    def selected_field_path(self) -> tuple[str, ...] | None:
        item = self.currentItem()
        if item is None:
            return None
        if item.data(0, self.IS_FIELD_ROLE) is not True:
            return None
        field_path: object = item.data(0, self.FIELD_PATH_ROLE)
        if not isinstance(field_path, tuple):
            return None
        path_parts = cast(tuple[object, ...], field_path)
        if not all(isinstance(path_part, str) for path_part in path_parts):
            return None
        return cast(tuple[str, ...], path_parts)

    def _deep_tree_from_message_dict(
        self,
        values: TreeValue,
        get_display_value: Callable[[TreeValue], str | None] | None,
        parent: QTreeWidgetItem | None = None,
        base_qtree: TreeWidget | None = None,
        field_path: tuple[str, ...] = (),
    ) -> None:
        if not isinstance(values, dict):
            widget_item = QTreeWidgetItem([f"{values}"])
            self._set_item_field_data(
                widget_item,
                field_path=field_path,
                is_field=False,
            )
            if parent is not None:
                parent.addChild(widget_item)
        else:
            for key, value in values.items():
                current_field_path = (*field_path, key)
                if get_display_value:
                    display_value = get_display_value(value)
                    if display_value is not None:
                        value = display_value
                if isinstance(value, dict):
                    widget_item = QTreeWidgetItem([f"{key}"])
                    self._deep_tree_from_message_dict(
                        value,
                        get_display_value,
                        widget_item,
                        field_path=current_field_path,
                    )
                elif isinstance(value, list):
                    widget_item = QTreeWidgetItem([f"{key}"])
                    for index, _value in enumerate(value):
                        index_item = self._list_index_item(
                            index, _value, get_display_value, current_field_path
                        )
                        widget_item.addChild(index_item)
                else:
                    widget_item = QTreeWidgetItem([f"{key} = {value}"])
                self._set_item_field_data(
                    widget_item,
                    field_path=current_field_path,
                    is_field=True,
                )
                if parent is not None:
                    parent.addChild(widget_item)
                elif base_qtree is not None:
                    base_qtree.addTopLevelItem(widget_item)

    def _list_index_item(
        self,
        index: int,
        value: TreeValue,
        get_display_value: Callable[[TreeValue], str | None] | None,
        field_path: tuple[str, ...],
    ) -> QTreeWidgetItem:
        if get_display_value:
            display_value = get_display_value(value)
            if display_value is not None:
                value = display_value

        if isinstance(value, dict):
            index_item = QTreeWidgetItem([f"{index}"])
            self._deep_tree_from_message_dict(
                value,
                get_display_value,
                index_item,
                field_path=field_path,
            )
        elif isinstance(value, list):
            index_item = QTreeWidgetItem([f"{index}"])
            for child_index, child_value in enumerate(value):
                index_item.addChild(
                    self._list_index_item(
                        child_index,
                        child_value,
                        get_display_value,
                        field_path,
                    )
                )
        else:
            index_item = QTreeWidgetItem([f"{index} = {value}"])

        self._set_item_field_data(
            index_item,
            field_path=field_path,
            is_field=False,
        )
        return index_item

    def _set_item_field_data(
        self,
        item: QTreeWidgetItem,
        field_path: tuple[str, ...],
        is_field: bool,
    ) -> None:
        item.setData(0, self.FIELD_PATH_ROLE, field_path)
        item.setData(0, self.IS_FIELD_ROLE, is_field)
