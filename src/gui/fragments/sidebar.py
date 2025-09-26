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
        """
        Parameters
        ----------
        parent: widget
            parent widget

        showMenuButton: bool
            whether to show menu button

        showReturnButton: bool
            whether to show return button

        collapsible: bool
            Is the navigation interface collapsible
        """
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
        """insert navigation item

        Parameters
        ----------
        index: int
            insert position

        routKey: str
            the unique name of item

        icon: str | QIcon | FluentIconBase
            the icon of navigation item

        text: str
            the text of navigation item

        onClick: callable
            the slot connected to item clicked signal

        selectable: bool
            whether the item is selectable

        position: NavigationItemPosition
            where the item is added

        tooltip: str
            the tooltip of item

        parentRouteKey: str
            the route key of parent item, the parent item should be `NavigationTreeWidgetBase`
        """
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
        """insert custom widget

        Parameters
        ----------
        index: int
            insert position

        routKey: str
            the unique name of item

        widget: NavigationWidget
            the custom widget to be added

        onClick: callable
            the slot connected to item clicked signal

        position: NavigationItemPosition
            where the widget is added

        tooltip: str
            the tooltip of widget

        parentRouteKey: str
            the route key of parent item, the parent item should be `NavigationTreeWidgetBase`
        """
        self.panel.insertWidget(
            index,
            routeKey,
            widget,
            onClick,
            position,
            tooltip,
            parentRouteKey,
        )
