from PyQt6.QtGui import QResizeEvent
from PyQt6.QtWidgets import QHBoxLayout, QWidget
from qfluentwidgets import (
    FluentStyleSheet,
    FluentTitleBar,
    NavigationItemPosition,
    NavigationWidget,
    qrouter,
)
from qfluentwidgets.window.fluent_window import FluentWindowBase

from src.gui.components.qfluent_widget.no_animated_stacked_widget import (
    NoAnimatedStackedWidget,
)
from src.gui.fragments.sidebar import Sidebar


class AppFluentWindow(FluentWindowBase):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.stackedWidget = NoAnimatedStackedWidget()
        FluentStyleSheet.FLUENT_WINDOW.apply(self.stackedWidget)

        self.setTitleBar(FluentTitleBar(self))

        self.navigationInterface = Sidebar(self)
        self.widgetLayout = QHBoxLayout()

        self.hBoxLayout.addWidget(self.navigationInterface)
        self.hBoxLayout.addLayout(self.widgetLayout)
        self.hBoxLayout.setStretchFactor(self.widgetLayout, 1)

        self.widgetLayout.addWidget(self.stackedWidget)
        self.widgetLayout.setContentsMargins(0, 48, 0, 0)

        self.navigationInterface.displayModeChanged.connect(self.titleBar.raise_)
        self.titleBar.raise_()

    def addWidget(
        self,
        interface: QWidget,
        navigation_widget: NavigationWidget,
        position: NavigationItemPosition = NavigationItemPosition.TOP,
        parent: QWidget | None = None,
        isTransparent: bool = False,
    ) -> None:
        """add widget, the object name of `interface` should be set already
        before calling this method

        Parameters
        ----------
        interface: QWidget
            the subinterface to be added

        icon: FluentIconBase | QIcon | str
            the icon of navigation item

        text: str
            the text of navigation item

        position: NavigationItemPosition
            the position of navigation item

        parent: QWidget
            the parent of navigation item

        isTransparent: bool
            whether to use transparent background
        """
        if not interface.objectName():
            raise ValueError("The object name of `interface` can't be empty string.")
        if parent and not parent.objectName():
            raise ValueError("The object name of `parent` can't be empty string.")

        interface.setProperty("isStackedTransparent", isTransparent)
        self.stackedWidget.addWidget(interface)

        routeKey = interface.objectName()
        self.navigationInterface.addWidget(
            routeKey=routeKey,
            widget=navigation_widget,
            onClick=lambda: self.switchTo(interface),
            position=position,
            parentRouteKey=parent.objectName() if parent else None,
        )

        if self.stackedWidget.count() == 1:
            self.stackedWidget.currentChanged.connect(self._onCurrentInterfaceChanged)
            self.navigationInterface.setCurrentItem(routeKey)
            qrouter.setDefaultRouteKey(self.stackedWidget, routeKey)

        self._updateStackedBackground()

    def removeWidget(self, routeKey: str, interface: QWidget) -> None:
        self.navigationInterface.panel.removeWidget(routeKey)
        self.stackedWidget.removeWidget(interface)
        self._updateStackedBackground()

    def resizeEvent(self, a0: QResizeEvent | None) -> None:
        self.titleBar.move(46, 0)
        self.titleBar.resize(self.width() - 46, self.titleBar.height())
