from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QTextEdit, QWidget
from qfluentwidgets import (
    MessageBoxBase,
    PushButton,
    SingleDirectionScrollArea,
    SmoothMode,
    SubtitleLabel,
)

from src.gui.components.log_syntax_highlighter import LogSyntaxHighlighter


class ScrollableMessageBox(MessageBoxBase):
    def __init__(self, title: str, content: str, parent: QWidget):
        super().__init__(parent=parent)

        self.title_label = SubtitleLabel(title, parent=self)

        self.content_edit = QTextEdit(parent=self)
        self.content_edit.setReadOnly(True)
        self.content_edit.setPlainText(content)

        font = QFont("Consolas", 9)
        if not font.exactMatch():
            font = QFont("Courier New", 9)
        self.content_edit.setFont(font)

        self.content_edit.setStyleSheet("""
            QTextEdit {
                background-color: transparent;
                color: white;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
                padding: 8px;
            }
        """)

        self.highlighter = LogSyntaxHighlighter(self.content_edit.document())

        self.copy_button = PushButton("Copier dans le presse-papier", self)
        self.copy_button.clicked.connect(lambda: self._copy_to_clipboard(content))

        scroll_area = SingleDirectionScrollArea(self)
        scroll_area.setSmoothMode(SmoothMode.NO_SMOOTH)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.content_edit)
        scroll_area.enableTransparentBackground()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumHeight(600)

        self.viewLayout.addWidget(self.title_label)
        self.viewLayout.addWidget(self.copy_button)
        self.viewLayout.addWidget(scroll_area)

    def _copy_to_clipboard(self, text: str):
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
