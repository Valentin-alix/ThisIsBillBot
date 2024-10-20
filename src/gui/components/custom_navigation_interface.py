from typing import Union
from PyQt5.QtGui import QIcon
from qfluentwidgets import (
    FluentIconBase,
    NavigationInterface,
    NavigationItemPosition,
    NavigationTreeWidget,
)


class CustomNavigationInterface(NavigationInterface):
    def insertItem(
        self,
        index: int,
        routeKey: str,
        icon: Union[str, QIcon, FluentIconBase],
        text: str,
        onClick=None,
        selectable=True,
        position=NavigationItemPosition.TOP,
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
            tooltip,  # type: ignore
            parentRouteKey,
        )
        # self.setMinimumHeight(self.panel.layoutMinHeight())
        return _widget  # type: ignore
