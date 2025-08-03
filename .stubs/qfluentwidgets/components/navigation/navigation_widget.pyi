from typing import Any

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QWidget
from qfluentwidgets import FluentIconBase
from qfluentwidgets import NavigationWidget as NavigationWidget

class NavigationToolButton(QWidget):
    clicked: pyqtSignal
    def __init__(
        self,
        icon: str | QIcon | FluentIconBase,
        parent: QWidget | None = None,
    ) -> None: ...
    def setToolTip(self, tooltip: str) -> None: ...
    def installEventFilter(self, filter: Any) -> None: ...
    def setVisible(self, visible: bool) -> None: ...
    def setDisabled(self, disabled: bool) -> None: ...
    clicked: Any  # pyqtSignal
