from typing import Any

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QMenu, QWidget
from qfluentwidgets import ComboBox as ComboBox
from qfluentwidgets import FluentIconBase

class ComboItem:
    text: str
    icon: str | QIcon | FluentIconBase | None
    userData: Any
    isEnabled: bool
    def __init__(
        self,
        text: str,
        icon: str | QIcon | FluentIconBase | None = None,
        userData: Any = None,
        isEnabled: bool = True,
    ) -> None: ...

class ComboBoxMenu(QMenu):
    view: Any
    isSubMenu: bool
    closedSignal: pyqtSignal
    _actions: list[Any]
    def __init__(self, parent: QWidget | None = None) -> None: ...
    def clear(self) -> None: ...
    def exec(self, pos: Any) -> None: ...
    def _closeParentMenu(self) -> None: ...
    def _hideMenu(self, hideForClose: bool = True) -> None: ...
    def _onItemClicked(self, item: Any) -> None: ...
    def adjustSize(self) -> None: ...
    def setAttribute(self, *args: Any) -> None: ...
