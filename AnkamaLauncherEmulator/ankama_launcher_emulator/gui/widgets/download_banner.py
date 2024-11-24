import re

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QVBoxLayout, QWidget
from qfluentwidgets import BodyLabel, CaptionLabel, ProgressBar

_STEP_RE = re.compile(r"(\d+)\s*/\s*(\d+)")


class DownloadBanner(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 6, 0, 4)
        layout.setSpacing(4)

        title = BodyLabel("Game is not up to date, downloading update...")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        self._progress_bar = ProgressBar()
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setValue(0)
        layout.addWidget(self._progress_bar)

        self._progress_label = CaptionLabel("")
        self._progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._progress_label)

        self.setVisible(False)

    def set_status(self, text: str) -> None:
        if not text:
            self.setVisible(False)
            self._progress_bar.setRange(0, 100)
            self._progress_bar.setValue(0)
            return
        self.setVisible(True)
        self._progress_label.setText(text)
        match = _STEP_RE.search(text)
        if match:
            current, total = int(match.group(1)), int(match.group(2))
            if total > 0:
                self._progress_bar.setRange(0, total)
                self._progress_bar.setValue(current)
