import binascii

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColorConstants, QPalette, QColor
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QTextEdit
from qfluentwidgets import FluentIcon, TransparentToolButton, FluentThemeColor

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

        background_color = FluentThemeColor.GRAY_DARK
        text_color = QColorConstants.White
        self.raw_content_label = QTextEdit()
        palette = self.raw_content_label.palette()
        palette.setColor(QPalette.Base, QColor(background_color.value))
        palette.setColor(QPalette.Text, QColor(text_color))
        self.raw_content_label.setPalette(palette)
        self.raw_content_label.setFixedHeight(100)
        self.raw_content_label.setReadOnly(True)
        self.layout().addWidget(self.raw_content_label)

    def set_content(self, msg_json: dict, raw_content: bytes):
        self.dynamic_tree.set_content(msg_json)
        self.raw_content_label.setText(binascii.hexlify(raw_content).decode("utf-8"))
