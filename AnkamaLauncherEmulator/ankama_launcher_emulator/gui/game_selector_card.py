from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QMouseEvent, QPixmap
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel

COLOR = QColor("#00470E")
COLOR_ACTIVE = COLOR.lighter(200).name()
COLOR_INACTIVE = COLOR.darker(200).name()
COLOR_UNAVAILABLE = QColor("#3a3a3a").name()


class GameSelectorCard(QFrame):
    clicked = pyqtSignal()

    def __init__(
        self, title: str, logo_path: Path, is_active: bool, available: bool = True, parent=None
    ):
        super().__init__(parent)
        self._available = available
        self.setCursor(
            Qt.CursorShape.PointingHandCursor
            if available
            else Qt.CursorShape.ForbiddenCursor
        )
        self.setMinimumHeight(72)
        self._setup_ui(title, logo_path)
        self.set_active(is_active)

    def _setup_ui(self, title: str, logo_path: Path) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(14)

        logo = QLabel()
        pixmap = QPixmap(str(logo_path)).scaled(
            48,
            48,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        logo.setPixmap(pixmap)
        logo.setFixedSize(48, 48)
        layout.addWidget(logo)

        self._title_label = QLabel(title)
        font = self._title_label.font()
        font.setPointSize(12)
        font.setWeight(QFont.Weight.DemiBold)
        self._title_label.setFont(font)
        layout.addWidget(self._title_label, 1)

    def set_active(self, active: bool) -> None:
        if not self._available:
            bg = COLOR_UNAVAILABLE
        else:
            bg = COLOR_ACTIVE if active else COLOR_INACTIVE
        self.setStyleSheet(
            f"GameSelectorCard {{ background-color: {bg}; border-radius: 8px; }}"
        )
        self.setGraphicsEffect(None)
        if not self._available:
            from PyQt6.QtWidgets import QGraphicsOpacityEffect
            effect = QGraphicsOpacityEffect(self)
            effect.setOpacity(0.45)
            self.setGraphicsEffect(effect)

    def mousePressEvent(self, a0: QMouseEvent | None) -> None:
        if a0 is not None and a0.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(a0)
