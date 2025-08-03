from collections.abc import Callable
from enum import Enum
from typing import Any

from PyQt6.QtCore import QObject
from PyQt6.QtWidgets import QVBoxLayout, QWidget
from qfluentwidgets import NavigationWidget

class NavigationDisplayMode(Enum):
    COMPACT = 0
    EXPAND = 1
    MENU = 2
    MINIMAL = 3

class NavigationItem:
    routeKey: str
    parentRouteKey: str | None
    widget: NavigationWidget
    def __init__(
        self, routeKey: str, parentRouteKey: str | None, widget: NavigationWidget
    ) -> None: ...

class NavigationItemLayout(QVBoxLayout):
    def __init__(self, parent: QWidget | None = None) -> None: ...

class NavigationToolTipFilter(QObject):
    def __init__(self, parent: QWidget, showDelay: int = 300) -> None: ...

class NavigationTreeWidgetBase(NavigationWidget):
    def isRoot(self) -> bool: ...
    def isLeaf(self) -> bool: ...
    def setExpanded(self, isExpanded: bool) -> None: ...
    def insertChild(self, index: int, widget: NavigationWidget) -> None: ...
    def removeChild(self, widget: NavigationWidget) -> None: ...

class NavigationFlyoutMenu(QWidget):
    expanded: Any  # pyqtSignal
    def __init__(self, widget: Any, parent: QWidget | None = None) -> None: ...

class NavigationPanel(QWidget):
    displayModeChanged: Any
    items: dict[str, NavigationItem]
    def insertItem(
        self,
        index: int,
        routeKey: str,
        icon: str | Any,
        text: str,
        onClick: Callable[[], None] | None = None,
        selectable: bool = True,
        position: NavigationDisplayMode | Any = ...,
        tooltip: str | None = None,
        parentRouteKey: str | None = None,
    ) -> NavigationTreeWidgetBase | None: ...
    def insertWidget(
        self,
        index: int,
        routeKey: str,
        widget: NavigationWidget,
        onClick: Callable[[], None] | None = None,
        position: Any = ...,
        tooltip: str | None = None,
        parentRouteKey: str | None = None,
    ) -> None: ...
