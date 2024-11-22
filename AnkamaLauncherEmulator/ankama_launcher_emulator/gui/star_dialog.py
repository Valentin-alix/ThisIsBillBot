import json
import os

from PyQt6.QtCore import Qt, QTimer, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import (
    QHBoxLayout,
)
from qfluentwidgets import (
    BodyLabel,
    CardWidget,
)

from ankama_launcher_emulator.consts import (
    APP_CONFIG_PATH,
    GITHUB_URL,
)


class SystemRequirementCard(CardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.infoLabel = BodyLabel(
            "This tools helped you ? Put a ⭐ on GitHub !", self
        )

        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.setContentsMargins(20, 11, 11, 11)
        self.hBoxLayout.setSpacing(15)

        self.setFixedHeight(50)

        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)

        self.hBoxLayout.addWidget(self.infoLabel, 0, Qt.AlignmentFlag.AlignCenter)

        self.clicked.connect(self.open_and_dismiss)

    def dismiss(self) -> None:
        mark_star_repo_shown()
        QTimer.singleShot(0, self.hide)

    def open_and_dismiss(self) -> None:
        QDesktopServices.openUrl(QUrl(GITHUB_URL))
        self.dismiss()


def has_shown_star_repo() -> bool:
    if not os.path.exists(APP_CONFIG_PATH):
        return False
    with open(APP_CONFIG_PATH, "r") as file:
        try:
            config = json.load(file)
        except (json.JSONDecodeError, ValueError):
            return False
    return config.get("star_repo_shown", False)


def mark_star_repo_shown() -> None:
    config: dict = {}
    if os.path.exists(APP_CONFIG_PATH):
        with open(APP_CONFIG_PATH, "r") as f:
            try:
                config = json.load(f)
            except (json.JSONDecodeError, ValueError):
                config = {}
    config["star_repo_shown"] = True
    with open(APP_CONFIG_PATH, "w") as f:
        json.dump(config, f)
