from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QHBoxLayout
from qfluentwidgets import BodyLabel


class PropertyWidget(QWidget):
    def __init__(self, key: str, value: str):
        super().__init__()
        self._hbox_layout = QHBoxLayout()
        self.setLayout(self._hbox_layout)
        label_header = BodyLabel(text=key + " : ")
        self._hbox_layout.addWidget(label_header)

        self.label_widget: BodyLabel | None = None
        self.set_content_value(value)

    def set_content_value(self, value: str):
        if self.label_widget is None:
            self.label_widget = BodyLabel(text=value)
            self.label_widget.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            self._hbox_layout.addWidget(self.label_widget)
        else:
            self.label_widget.setText(value)
