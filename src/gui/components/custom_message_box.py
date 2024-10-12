from PyQt5.QtWidgets import QWidget
from qfluentwidgets import (
    SubtitleLabel,
    BodyLabel,
    SingleDirectionScrollArea,
    SmoothMode,
    TextWrap,
    MessageBoxBase,
)


class CustomMessageBox(MessageBoxBase):
    def __init__(self, title: str, content: str, parent: QWidget):
        super().__init__(parent=parent)

        self.title_label = SubtitleLabel(title, parent=self)
        self.content_label = BodyLabel(text=content, parent=self)
        if self.isWindow():
            if self.parent():
                content_width = max(self.title_label.width(), self.parent().width())
                chars = max(min(content_width / 9, 140), 30)
            else:
                chars = 100
        else:
            content_width = max(self.title_label.width(), self.window().width())
            chars = max(min(content_width / 9, 100), 30)
        self.content_label.setText(TextWrap.wrap(content, chars, False)[0])

        scroll_area = SingleDirectionScrollArea(self)
        scroll_area.setSmoothMode(SmoothMode.NO_SMOOTH)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.content_label)
        scroll_area.enableTransparentBackground()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumHeight(600)

        self.viewLayout.addWidget(self.title_label)
        self.viewLayout.addWidget(scroll_area)
