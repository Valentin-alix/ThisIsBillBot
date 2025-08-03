from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget
from qfluentwidgets import BodyLabel, CaptionLabel


class PropertyWidget(QWidget):
    def __init__(
        self,
        key: str,
        value: str,
        vertical: bool = False,
        parent: QWidget | None = None,
    ):
        super().__init__(parent=parent)

        if vertical:
            layout = QVBoxLayout()
            layout.setContentsMargins(0, 2, 0, 2)
            layout.setSpacing(0)
            label_header = CaptionLabel(text=key, parent=self)
        else:
            layout = QHBoxLayout()
            label_header = BodyLabel(text=key + " : ", parent=self)

        self._layout = layout
        self.setLayout(layout)
        layout.addWidget(label_header)

        self.label_widget: BodyLabel | None = None
        self.set_content_value(value)

    def set_content_value(self, value: str):
        if self.label_widget is None:
            label_widget = BodyLabel(text=value, parent=self)
            label_widget.setWordWrap(True)
            label_widget.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            self._layout.addWidget(label_widget)
            self.label_widget = label_widget
        else:
            self.label_widget.setText(value)
