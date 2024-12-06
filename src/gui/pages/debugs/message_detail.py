from typing import Any

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush, QColor
from PyQt6.QtWidgets import QHBoxLayout, QTreeWidgetItem, QVBoxLayout, QWidget
from qfluentwidgets import FluentIcon, LineEdit, SmoothMode, TransparentToolButton

from src.gui.components.qfluent_widget.dynamic_tree_widget import DynamicTreeWidget


class MessageDetailWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        self._layout = QVBoxLayout()
        self.setLayout(self._layout)
        self._layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        top_bar = QWidget(self)
        top_bar_layout = QHBoxLayout()
        top_bar.setLayout(top_bar_layout)
        self._layout.addWidget(top_bar)

        self.quit_btn = TransparentToolButton(FluentIcon.CLOSE, top_bar)
        top_bar_layout.addWidget(self.quit_btn)

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
    ) -> None:
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
