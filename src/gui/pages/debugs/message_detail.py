from typing import Any

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget
from qfluentwidgets import FluentIcon, SmoothMode, TransparentToolButton

from src.gui.components.qfluent_widget.dynamic_tree_widget import DynamicTreeWidget


class MessageDetailWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignHCenter)

        self.quit_btn = TransparentToolButton(FluentIcon.CLOSE)
        self.layout().addWidget(self.quit_btn)

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
