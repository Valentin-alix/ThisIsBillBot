from PyQt5.QtWidgets import QVBoxLayout, QWidget, QFrame
from qfluentwidgets import SubtitleLabel


class GroupBox(QFrame):
    def __init__(self, title: str):
        super().__init__()
        self.setFrameStyle(QFrame.Box | QFrame.Raised)

        layout = QVBoxLayout()

        title_label = SubtitleLabel(text=title)
        layout.addWidget(title_label)

        self.content_layout = QVBoxLayout()
        layout.addLayout(self.content_layout)

        self.setLayout(layout)

    def add_widget(self, widget: QWidget):
        self.content_layout.addWidget(widget)
