from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QResizeEvent
from PyQt6.QtWidgets import QWidget
from qfluentwidgets import CaptionLabel, SplashScreen


class StartupSplashScreen(SplashScreen):
    _ICON_HEIGHT = 102

    def __init__(self, icon: QIcon, parent: QWidget) -> None:
        super().__init__(icon, parent)
        self._status_label = CaptionLabel(parent=self)
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def set_status(self, status: str) -> None:
        self._status_label.setText(status)
        self._position_status_label()

    def resizeEvent(self, a0: QResizeEvent | None) -> None:
        super().resizeEvent(a0)
        self._position_status_label()

    def _position_status_label(self) -> None:
        height = self._status_label.sizeHint().height()
        self._status_label.setGeometry(
            0,
            self.height() // 2 + self._ICON_HEIGHT // 2 + 16,
            self.width(),
            height,
        )
