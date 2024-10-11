import binascii
from typing import Any

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout, QWidget
from qfluentwidgets import FluentIcon, TransparentToolButton, TextEdit
from qfluentwidgets import SmoothMode

from src.gui.components.dynamic_tree_widget import DynamicTreeWidget


class MessageDetailWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignHCenter)

        self.quit_btn = TransparentToolButton(FluentIcon.CLOSE)
        self.layout().addWidget(self.quit_btn)

        self.dynamic_tree = DynamicTreeWidget()

        self.dynamic_tree.scrollDelagate.verticalSmoothScroll.setSmoothMode(
            SmoothMode.NO_SMOOTH
        )
        self.layout().addWidget(self.dynamic_tree)

        self.raw_content_label = TextEdit()
        self.raw_content_label.setFixedHeight(75)
        self.raw_content_label.setReadOnly(True)
        self.layout().addWidget(self.raw_content_label)

    def set_content(self, msg_json: dict[str, Any], raw_content: bytes):
        self.dynamic_tree.set_content(msg_json)
        self.raw_content_label.setText(binascii.hexlify(raw_content).decode())
