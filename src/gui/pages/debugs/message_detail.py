from typing import Any

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtWidgets import QHBoxLayout, QTreeWidgetItem, QVBoxLayout, QWidget
from qfluentwidgets import FluentIcon, LineEdit, SmoothMode, TransparentToolButton

from src.gui.components.qfluent_widget.dynamic_tree_widget import DynamicTreeWidget


class MessageDetailWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignHCenter)

        top_bar = QWidget()
        top_bar.setLayout(QHBoxLayout())
        self.layout().addWidget(top_bar)

        self.quit_btn = TransparentToolButton(FluentIcon.CLOSE)
        top_bar.layout().addWidget(self.quit_btn)

        self.search_bar = LineEdit()
        self.search_bar.setPlaceholderText("Rechercher dans le contenu...")
        self.search_bar.setClearButtonEnabled(True)
        self.search_bar.textChanged.connect(self._on_search_text_changed)
        top_bar.layout().addWidget(self.search_bar)

        trees_widget = QWidget()
        trees_widget.setLayout(QHBoxLayout())
        self.layout().addWidget(trees_widget)

        self.dynamic_tree = DynamicTreeWidget()
        self.dynamic_tree.scrollDelagate.verticalSmoothScroll.setSmoothMode(
            SmoothMode.NO_SMOOTH
        )
        trees_widget.layout().addWidget(self.dynamic_tree)

        self.obf_dynamic_tree = DynamicTreeWidget()
        self.obf_dynamic_tree.scrollDelagate.verticalSmoothScroll.setSmoothMode(
            SmoothMode.NO_SMOOTH
        )
        trees_widget.layout().addWidget(self.obf_dynamic_tree)

    def set_content(
        self,
        msg_json: dict[str, Any] | None,
        obf_msg_json: dict[str, Any] | None,
    ):
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

    def _on_search_text_changed(self, text: str):
        text = text.strip()
        if not text:
            self._clear_search()
        elif len(text) >= 2:
            self._search_and_expand(self.dynamic_tree, text.lower())
            self._search_and_expand(self.obf_dynamic_tree, text.lower())

    def _clear_search(self):
        self._reset_tree_highlighting(self.dynamic_tree)
        self._reset_tree_highlighting(self.obf_dynamic_tree)

        self.dynamic_tree.collapseAll()
        self.dynamic_tree.expandToDepth(1)
        self.obf_dynamic_tree.collapseAll()
        self.obf_dynamic_tree.expandToDepth(1)

    def _search_and_expand(self, tree: DynamicTreeWidget, search_text: str):
        self._reset_tree_highlighting(tree)
        tree.collapseAll()

        found_items: list[QTreeWidgetItem] = []
        self._find_matching_items(tree.invisibleRootItem(), search_text, found_items)

        for item in found_items:
            item.setBackground(0, QBrush(QColor(255, 255, 0, 100)))
            self._expand_to_item(item)

    def _find_matching_items(
        self,
        parent: QTreeWidgetItem,
        search_text: str,
        found_items: list[QTreeWidgetItem]
    ):
        for i in range(parent.childCount()):
            child = parent.child(i)
            if search_text in child.text(0).lower():
                found_items.append(child)

            self._find_matching_items(child, search_text, found_items)

    def _expand_to_item(self, item: QTreeWidgetItem):
        parent = item.parent()
        while parent is not None:
            parent.setExpanded(True)
            parent = parent.parent()
        item.setExpanded(True)

    def _reset_tree_highlighting(self, tree: DynamicTreeWidget):
        self._reset_item_highlighting(tree.invisibleRootItem())

    def _reset_item_highlighting(self, parent: QTreeWidgetItem):
        for i in range(parent.childCount()):
            child = parent.child(i)
            child.setBackground(0, QBrush())
            self._reset_item_highlighting(child)
