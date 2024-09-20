from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout, QWidget
from qfluentwidgets import FluentIcon, TransparentToolButton

from src.gui.components.tree import DynamicTreeWidget


class MessageDetailWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignHCenter)

        self.quit_btn = TransparentToolButton(FluentIcon.CLOSE)
        self.layout().addWidget(self.quit_btn)

        self.dynamic_tree = DynamicTreeWidget()
        self.layout().addWidget(self.dynamic_tree)

    def set_content(self, msg_json: dict):
        self.dynamic_tree.set_content(msg_json)
