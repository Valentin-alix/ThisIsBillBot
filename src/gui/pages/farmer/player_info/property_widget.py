from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QHBoxLayout
from qfluentwidgets import BodyLabel


class PropertyWidget(QWidget):
    def __init__(self, key: str, value: str, parent: QWidget | None = None):
        super().__init__(parent=parent)
        self._hbox_layout = QHBoxLayout()
        self.setLayout(self._hbox_layout)
        label_header = BodyLabel(text=key + " : ", parent=self)
        self._hbox_layout.addWidget(label_header)

        self.label_widget: BodyLabel | None = None
        self.set_content_value(value)

    def set_content_value(self, value: str):
        if self.label_widget is None:
            label_widget = BodyLabel(text=value, parent=self)
            label_widget.setTextInteractionFlags(
                Qt.TextInteractionFlag.TextSelectableByMouse
            )
            self._hbox_layout.addWidget(label_widget)
            self.label_widget = label_widget
        else:
            self.label_widget.setText(value)
