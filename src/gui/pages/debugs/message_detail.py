from dataclasses import dataclass
from typing import Any, cast

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush, QColor
from PyQt6.QtWidgets import QHBoxLayout, QTreeWidgetItem, QVBoxLayout, QWidget
from google.protobuf.descriptor import Descriptor, FieldDescriptor
from qfluentwidgets import (
    FluentIcon,
    LineEdit,
    PrimaryPushButton,
    SmoothMode,
    TransparentToolButton,
)

from src.gui.components.qfluent_widget.dynamic_tree_widget import DynamicTreeWidget

ABSENT_FIELD_DISPLAY_VALUE = "<absent>"


@dataclass(frozen=True)
class SelectedPinnedField:
    container_descriptor: Descriptor | None
    field_name: str
    path: tuple[str, ...]

    @property
    def path_label(self) -> str:
        return ".".join(self.path)


def complete_message_tree_content(
    content: dict[str, Any],
    descriptor: Descriptor | None,
) -> dict[str, Any]:
    if descriptor is None:
        return content

    completed: dict[str, Any] = {}
    for field_descriptor in descriptor.fields:
        field_name = field_descriptor.name
        if field_name not in content:
            completed[field_name] = ABSENT_FIELD_DISPLAY_VALUE
            continue
        completed[field_name] = _complete_message_tree_value(
            content[field_name], field_descriptor
        )

    for field_name, value in content.items():
        if field_name not in completed:
            completed[field_name] = value

    return completed


def _complete_message_tree_value(value: Any, field_descriptor: FieldDescriptor) -> Any:
    message_type = cast(Descriptor | None, field_descriptor.message_type)
    if message_type is None or field_descriptor.type != FieldDescriptor.TYPE_MESSAGE:
        return value

    if getattr(field_descriptor, "label") == FieldDescriptor.LABEL_REPEATED:
        if not isinstance(value, list):
            return value
        value_items = cast(list[Any], value)
        return [
            complete_message_tree_content(cast(dict[str, Any], item), message_type)
            if isinstance(item, dict)
            else item
            for item in value_items
        ]

    if isinstance(value, dict):
        return complete_message_tree_content(cast(dict[str, Any], value), message_type)
    return value


def resolve_selected_pinned_field(
    root_descriptor: Descriptor,
    field_path: tuple[str, ...],
) -> SelectedPinnedField | None:
    if not field_path:
        return None

    container_descriptor = root_descriptor
    for parent_field_name in field_path[:-1]:
        parent_field = container_descriptor.fields_by_name.get(parent_field_name)
        if parent_field is None:
            return None
        next_descriptor = _message_field_descriptor(parent_field)
        if next_descriptor is None:
            return None
        container_descriptor = next_descriptor

    field_name = field_path[-1]
    if field_name not in container_descriptor.fields_by_name:
        return None
    return SelectedPinnedField(
        container_descriptor=container_descriptor,
        field_name=field_name,
        path=field_path,
    )


def _message_field_descriptor(field_descriptor: FieldDescriptor) -> Descriptor | None:
    if field_descriptor.type != FieldDescriptor.TYPE_MESSAGE:
        return None
    return cast(Descriptor | None, field_descriptor.message_type)


class MessageDetailWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        self._msg_json: dict[str, Any] | None = None
        self._obf_msg_json: dict[str, Any] | None = None
        self._msg_descriptor: Descriptor | None = None
        self._obf_msg_descriptor: Descriptor | None = None

        self._layout = QVBoxLayout()
        self.setLayout(self._layout)
        self._layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        top_bar = QWidget(self)
        top_bar_layout = QHBoxLayout()
        top_bar.setLayout(top_bar_layout)
        self._layout.addWidget(top_bar)

        self.quit_btn = TransparentToolButton(FluentIcon.CLOSE, top_bar)
        top_bar_layout.addWidget(self.quit_btn)

        self.lock_pinned_fields_btn = PrimaryPushButton(
            FluentIcon.PIN, "Lock pinned fields", top_bar
        )
        top_bar_layout.addWidget(self.lock_pinned_fields_btn)

        self.show_absent_fields_btn = TransparentToolButton(FluentIcon.VIEW, top_bar)
        self.show_absent_fields_btn.setCheckable(True)
        self.show_absent_fields_btn.setToolTip("Afficher les champs absents")
        self.show_absent_fields_btn.clicked.connect(self._on_show_absent_fields_clicked)
        top_bar_layout.addWidget(self.show_absent_fields_btn)

        self.search_bar = LineEdit(top_bar)
        self.search_bar.setPlaceholderText("Rechercher dans le contenu...")
        self.search_bar.setClearButtonEnabled(True)
        self.search_bar.textChanged.connect(self._on_search_text_changed)
        top_bar_layout.addWidget(self.search_bar)

        trees_widget = QWidget(self)
        trees_widget_layout = QHBoxLayout()
        trees_widget.setLayout(trees_widget_layout)
        self._layout.addWidget(trees_widget)

        self.dynamic_tree = DynamicTreeWidget(trees_widget)
        self.dynamic_tree.scrollDelagate.verticalSmoothScroll.setSmoothMode(
            SmoothMode.NO_SMOOTH
        )
        trees_widget_layout.addWidget(self.dynamic_tree)

        self.obf_dynamic_tree = DynamicTreeWidget(trees_widget)
        self.obf_dynamic_tree.scrollDelagate.verticalSmoothScroll.setSmoothMode(
            SmoothMode.NO_SMOOTH
        )
        trees_widget_layout.addWidget(self.obf_dynamic_tree)

    def set_content(
        self,
        msg_json: dict[str, Any] | None,
        obf_msg_json: dict[str, Any] | None,
        msg_descriptor: Descriptor | None = None,
        obf_msg_descriptor: Descriptor | None = None,
    ) -> None:
        self._msg_json = msg_json
        self._obf_msg_json = obf_msg_json
        self._msg_descriptor = msg_descriptor
        self._obf_msg_descriptor = obf_msg_descriptor
        self._render_content()

    def _render_content(self) -> None:
        msg_json = self._display_content(self._msg_json, self._msg_descriptor)
        obf_msg_json = self._display_content(
            self._obf_msg_json, self._obf_msg_descriptor
        )
        if msg_json is not None:
            self.dynamic_tree.show()
            self.dynamic_tree.set_content(msg_json)
        else:
            self.dynamic_tree.hide()
        if obf_msg_json is not None:
            self.obf_dynamic_tree.show()
            self.obf_dynamic_tree.set_content(obf_msg_json)
        else:
            self.obf_dynamic_tree.hide()
        self.lock_pinned_fields_btn.setEnabled(
            msg_json is not None and obf_msg_json is not None
        )
        self.show_absent_fields_btn.setEnabled(
            (self._msg_json is not None and self._msg_descriptor is not None)
            or (self._obf_msg_json is not None and self._obf_msg_descriptor is not None)
        )

    def _display_content(
        self, content: dict[str, Any] | None, descriptor: Descriptor | None
    ) -> dict[str, Any] | None:
        if content is None:
            return None
        if not self.show_absent_fields_btn.isChecked():
            return content
        return complete_message_tree_content(content, descriptor)

    def _on_show_absent_fields_clicked(self) -> None:
        if self.show_absent_fields_btn.isChecked():
            cast(Any, self.show_absent_fields_btn).setIcon(FluentIcon.HIDE)
            self.show_absent_fields_btn.setToolTip("Masquer les champs absents")
        else:
            cast(Any, self.show_absent_fields_btn).setIcon(FluentIcon.VIEW)
            self.show_absent_fields_btn.setToolTip("Afficher les champs absents")
        self._render_content()

    def selected_pinned_fields(
        self,
    ) -> tuple[SelectedPinnedField, SelectedPinnedField] | None:
        non_obf_field = self._selected_pinned_field(
            self.dynamic_tree, self._msg_descriptor
        )
        obf_field = self._selected_pinned_field(
            self.obf_dynamic_tree, self._obf_msg_descriptor
        )
        if non_obf_field is None or obf_field is None:
            return None
        return obf_field, non_obf_field

    def _selected_pinned_field(
        self,
        tree: DynamicTreeWidget,
        descriptor: Descriptor | None,
    ) -> SelectedPinnedField | None:
        field_path = tree.selected_field_path()
        if field_path is None:
            return None
        if descriptor is None:
            if len(field_path) != 1:
                return None
            return SelectedPinnedField(
                container_descriptor=None,
                field_name=field_path[0],
                path=field_path,
            )
        return resolve_selected_pinned_field(descriptor, field_path)

    def _on_search_text_changed(self, text: str) -> None:
        text = text.strip()
        if not text:
            self._clear_search()
        elif len(text) >= 2:
            self._search_and_expand(self.dynamic_tree, text.lower())
            self._search_and_expand(self.obf_dynamic_tree, text.lower())

    def _clear_search(self) -> None:
        self._reset_tree_highlighting(self.dynamic_tree)
        self._reset_tree_highlighting(self.obf_dynamic_tree)

        self.dynamic_tree.collapseAll()
        self.dynamic_tree.expandToDepth(1)
        self.obf_dynamic_tree.collapseAll()
        self.obf_dynamic_tree.expandToDepth(1)

    def _search_and_expand(self, tree: DynamicTreeWidget, search_text: str) -> None:
        self._reset_tree_highlighting(tree)
        tree.collapseAll()

        found_items: list[QTreeWidgetItem] = []
        root = tree.invisibleRootItem()
        assert root is not None
        self._find_matching_items(root, search_text, found_items)

        for item in found_items:
            item.setBackground(0, QBrush(QColor(255, 255, 0, 100)))
            self._expand_to_item(item)

    def _find_matching_items(
        self,
        parent: QTreeWidgetItem | None,
        search_text: str,
        found_items: list[QTreeWidgetItem],
    ) -> None:
        if parent is None:
            return
        for i in range(parent.childCount()):
            child = parent.child(i)
            if child is None:
                continue
            if search_text in child.text(0).lower():
                found_items.append(child)

            self._find_matching_items(child, search_text, found_items)

    def _expand_to_item(self, item: QTreeWidgetItem) -> None:
        parent = item.parent()
        while parent is not None:
            parent.setExpanded(True)
            parent = parent.parent()
        item.setExpanded(True)

    def _reset_tree_highlighting(self, tree: DynamicTreeWidget) -> None:
        root = tree.invisibleRootItem()
        assert root is not None
        self._reset_item_highlighting(root)

    def _reset_item_highlighting(self, parent: QTreeWidgetItem | None) -> None:
        if parent is None:
            return
        for i in range(parent.childCount()):
            child = parent.child(i)
            if child is None:
                continue
            child.setBackground(0, QBrush())
            self._reset_item_highlighting(child)
