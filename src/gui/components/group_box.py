from PyQt6.QtWidgets import QVBoxLayout, QWidget, QFrame
from qfluentwidgets import SubtitleLabel


class GroupBox(QFrame):
    def __init__(self, title: str, parent: QWidget | None = None):
        super().__init__(parent=parent)

        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        title_label = SubtitleLabel(text=title, parent=self)
        layout.addWidget(title_label)

        self.content_layout = QVBoxLayout()
        layout.addLayout(self.content_layout)

        self.setLayout(layout)

    def add_widget(self, widget: QWidget):
        self.content_layout.addWidget(widget)
