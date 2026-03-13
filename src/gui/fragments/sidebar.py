from collections.abc import Callable

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QWidget
from qfluentwidgets import (
    FluentIconBase,
    NavigationInterface,
    NavigationItemPosition,
    NavigationTreeWidget,
    NavigationWidget,
)

from src.gui.fragments.sidebar_panel import SidebarPanel


class Sidebar(NavigationInterface):
    def __init__(
        self,
        parent: QWidget | None = None,
        showMenuButton: bool = True,
        showReturnButton: bool = False,
        collapsible: bool = True,
    ) -> None:
        super().__init__(parent=parent)
        self.panel = SidebarPanel(self)
        self.panel.setMenuButtonVisible(showMenuButton)
        self.panel.setReturnButtonVisible(showReturnButton)
        self.panel.setCollapsible(collapsible)
        self.panel.installEventFilter(self)
        self.panel.displayModeChanged.connect(self.displayModeChanged)

        self.resize(48, self.height())
        self.setMinimumWidth(48)
        self.panel.setExpandWidth(250)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def insertItem(
        self,
        index: int,
        routeKey: str,
        icon: str | QIcon | FluentIconBase,
        text: str,
        onClick: Callable[[], None] | None = None,
        selectable: bool = True,
        position: NavigationItemPosition = NavigationItemPosition.TOP,
        tooltip: str | None = None,
        parentRouteKey: str | None = None,
    ) -> NavigationTreeWidget:
        _widget = self.panel.insertItem(
            index,
            routeKey,
            icon,
            text,
            onClick,
            selectable,
            position,
            tooltip,
            parentRouteKey,
        )
        assert _widget
        return _widget

    def insertWidget(
        self,
        index: int,
        routeKey: str,
        widget: NavigationWidget,
        onClick: Callable[[], None] | None = None,
        position: NavigationItemPosition = NavigationItemPosition.TOP,
        tooltip: str | None = None,
        parentRouteKey: str | None = None,
    ) -> None:
        self.panel.insertWidget(
            index,
            routeKey,
            widget,
            onClick,
            position,
            tooltip,
            parentRouteKey,
        )
