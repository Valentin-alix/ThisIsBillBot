from enum import Enum
from typing import Any, Callable, overload, Union

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QIcon
from PyQt6.QtWidgets import (
    QDialog,
    QFrame,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QScrollArea,
    QTableView,
    QTableWidget,
    QTreeWidget,
    QVBoxLayout,
    QWidget,
)

from qfluentwidgets.components.widgets.scroll_bar import (
    SmoothScrollDelegate as SmoothScrollDelegate,
)

class SmoothMode(Enum):
    NO_SMOOTH = 0
    CONSTANT = 1
    LINEAR = 2
    QUADRATIC = 3
    COSINE = 4

class FluentIconBase:
    def icon(self, color: QColor | None = None) -> QIcon: ...
    def path(self) -> str: ...

class FluentIcon(FluentIconBase, Enum):
    ADD: FluentIcon
    BACK: FluentIcon
    CANCEL: FluentIcon
    CLOSE: FluentIcon
    COPY: FluentIcon
    COMMAND_PROMPT: FluentIcon
    CODE: FluentIcon
    DELETE: FluentIcon
    DOWNLOAD: FluentIcon
    EDIT: FluentIcon
    EMOJI_TAB_SYMBOLS: FluentIcon
    EXPOTE: FluentIcon
    FILTER: FluentIcon
    FOLDER: FluentIcon
    FONT: FluentIcon
    FULL_SCREEN: FluentIcon
    GLOBE: FluentIcon
    HEART: FluentIcon
    HELP: FluentIcon
    HIDE: FluentIcon
    HOME: FluentIcon
    INFO: FluentIcon
    LANGUAGE: FluentIcon
    LINK: FluentIcon
    MAIL: FluentIcon
    MANAGE_SEARCH: FluentIcon
    MENU: FluentIcon
    MINIMIZE: FluentIcon
    MORE: FluentIcon
    MOVE: FluentIcon
    MUSIC: FluentIcon
    MUTE: FluentIcon
    PALETTE: FluentIcon
    PAUSE: FluentIcon
    PEOPLE: FluentIcon
    PIN: FluentIcon
    PLAY: FluentIcon
    PRINT: FluentIcon
    RETURN: FluentIcon
    SAVE: FluentIcon
    SEARCH: FluentIcon
    SETTING: FluentIcon
    SHARE: FluentIcon
    SHOW: FluentIcon
    SPEED_HIGH: FluentIcon
    SPEED_MEDIUM: FluentIcon
    SPEED_OFF: FluentIcon
    TAG: FluentIcon
    SYNC: FluentIcon
    TRANSPARENT: FluentIcon
    UNPIN: FluentIcon
    UP: FluentIcon
    UPDATE: FluentIcon
    VIDEO: FluentIcon
    VIEW: FluentIcon
    VPN: FluentIcon
    ZOOM_IN: FluentIcon
    ZOOM_OUT: FluentIcon

class SingleDirectionScrollArea(QScrollArea):
    def __init__(
        self,
        parent: QWidget | None = None,
        orient: Qt.Orientation = Qt.Orientation.Vertical,
    ) -> None: ...
    def setSmoothMode(self, mode: SmoothMode) -> None: ...
    def enableTransparentBackground(self) -> None: ...
    def setVerticalScrollBarPolicy(self, policy: Qt.ScrollBarPolicy) -> None: ...
    def setHorizontalScrollBarPolicy(self, policy: Qt.ScrollBarPolicy) -> None: ...

class TableView(QTableView):
    scrollDelagate: SmoothScrollDelegate
    def __init__(self, parent: QWidget | None = None) -> None: ...

class TableWidget(QTableWidget):
    scrollDelagate: SmoothScrollDelegate
    def __init__(self, parent: QWidget | None = None) -> None: ...

class ListWidget(QListWidget):
    scrollDelegate: SmoothScrollDelegate
    def __init__(self, parent: QWidget | None = None) -> None: ...

class TreeWidget(QTreeWidget):
    scrollDelagate: SmoothScrollDelegate
    def __init__(self, parent: QWidget | None = None) -> None: ...

class ComboBox(QPushButton):
    currentIndexChanged: pyqtSignal
    items: list[Any]
    dropMenu: Any
    def __init__(self, parent: QWidget | None = None) -> None: ...
    def addItem(
        self,
        text: str,
        icon: Union[str, QIcon, FluentIconBase] | None = None,
        userData: Any = None,
    ) -> None: ...
    def addItems(self, texts: list[str]) -> None: ...
    def setCurrentText(self, text: str) -> None: ...
    def currentText(self) -> str: ...
    def currentData(self) -> Any: ...
    def findData(self, data: Any) -> int: ...
    def findText(self, text: str) -> int: ...
    def removeItem(self, index: int) -> None: ...
    def clear(self) -> None: ...
    def count(self) -> int: ...
    def currentIndex(self) -> int: ...
    def setCurrentIndex(self, index: int) -> None: ...
    def setText(self, text: str) -> None: ...
    def itemData(self, index: int) -> Any: ...

class PivotItem(QPushButton):
    @overload
    def __init__(self, parent: QWidget | None = None) -> None: ...
    @overload
    def __init__(self, text: str, parent: QWidget | None = None) -> None: ...

class Pivot(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None: ...
    def addItem(
        self,
        routeKey: str,
        text: str,
        onClick: Callable[[], None] | None = None,
        icon: Any = None,
    ) -> PivotItem | None: ...
    def insertItem(
        self,
        index: int,
        routeKey: str,
        text: str,
        onClick: Callable[[], None] | None = None,
        icon: Any = None,
    ) -> PivotItem | None: ...
    def addWidget(
        self,
        routeKey: str,
        widget: PivotItem,
        onClick: Callable[[], None] | None = None,
    ) -> None: ...
    def setCurrentItem(self, routeKey: str) -> None: ...

class SegmentedWidget(Pivot):
    def __init__(self, parent: QWidget | None = None) -> None: ...
    def addItem(
        self,
        routeKey: str,
        text: str,
        onClick: Callable[[], None] | None = None,
        icon: Union[str, QIcon, FluentIconBase] | None = None,
    ) -> PivotItem | None: ...  # type: ignore[override]
    def currentRouteKey(self) -> str: ...

class TransparentToolButton(QPushButton):
    def __init__(
        self,
        icon: Union[str, QIcon, FluentIconBase],
        parent: QWidget | None = None,
    ) -> None: ...

class PushButton(QPushButton):
    @overload
    def __init__(self, parent: QWidget | None = None) -> None: ...
    @overload
    def __init__(self, text: str, parent: QWidget | None = None) -> None: ...
    @overload
    def __init__(
        self,
        icon_or_text: Union[str, QIcon, FluentIconBase],
        text: str,
        parent: QWidget | None = None,
    ) -> None: ...

class PrimaryPushButton(PushButton):
    @overload
    def __init__(self, parent: QWidget | None = None) -> None: ...
    @overload
    def __init__(self, text: str, parent: QWidget | None = None) -> None: ...
    @overload
    def __init__(
        self,
        icon_or_text: Union[str, QIcon, FluentIconBase],
        text: str,
        parent: QWidget | None = None,
    ) -> None: ...

class SubtitleLabel(QLabel):
    @overload
    def __init__(self, parent: QWidget | None = None) -> None: ...
    @overload
    def __init__(self, text: str, parent: QWidget | None = None) -> None: ...

class BodyLabel(QLabel):
    @overload
    def __init__(self, parent: QWidget | None = None) -> None: ...
    @overload
    def __init__(self, text: str, parent: QWidget | None = None) -> None: ...

class CaptionLabel(QLabel):
    @overload
    def __init__(self, parent: QWidget | None = None) -> None: ...
    @overload
    def __init__(self, text: str, parent: QWidget | None = None) -> None: ...

class TitleLabel(QLabel):
    @overload
    def __init__(self, parent: QWidget | None = None) -> None: ...
    @overload
    def __init__(self, text: str, parent: QWidget | None = None) -> None: ...

class LineEdit(QLineEdit):
    def __init__(self, parent: QWidget | None = None) -> None: ...

class CardWidget(QFrame):
    clicked: pyqtSignal
    def __init__(self, parent: QWidget | None = None) -> None: ...

class ProgressBar(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None: ...
    def setRange(self, minimum: int, maximum: int) -> None: ...
    def setValue(self, value: int) -> None: ...

class MessageBoxBase(QDialog):
    viewLayout: QVBoxLayout
    def __init__(self, parent: QWidget | None = None) -> None: ...
    def reject(self) -> None: ...
    def exec(self) -> int: ...

class NavigationWidget(QWidget):
    EXPAND_WIDTH: int
    clicked: pyqtSignal
    isCompacted: bool
    isSelected: bool
    isPressed: bool
    isEnter: bool
    def __init__(
        self, isSelectable: bool = True, parent: QWidget | None = None
    ) -> None: ...
    def setCompacted(self, isCompacted: bool) -> None: ...
    def setSelected(self, isSelected: bool) -> None: ...
    def textColor(self) -> QColor: ...
    @property
    def isSelectable(self) -> bool: ...

class NavigationTreeWidget(NavigationWidget):
    def __init__(
        self,
        icon: Union[str, QIcon, FluentIconBase],
        text: str,
        isSelectable: bool = True,
        parent: QWidget | None = None,
    ) -> None: ...
    def isRoot(self) -> bool: ...
    def isLeaf(self) -> bool: ...
    def insertChild(self, index: int, widget: NavigationWidget) -> None: ...
    def removeChild(self, widget: NavigationWidget) -> None: ...
    def setExpanded(self, isExpanded: bool) -> None: ...
    def findChildren(self, *args: Any, **kwargs: Any) -> list[NavigationWidget]: ...  # type: ignore[override]

class NavigationSeparator(NavigationWidget): ...

class NavigationItemPosition(Enum):
    TOP = 0
    SCROLL = 1
    BOTTOM = 2

class NavigationDisplayMode(Enum):
    MINIMAL = 0
    COMPACT = 1
    EXPAND = 2
    MENU = 3

class Theme(Enum):
    LIGHT = 0
    DARK = 1
    AUTO = 2

class InfoBarPosition(Enum):
    TOP = 0
    BOTTOM = 1
    TOP_LEFT = 2
    TOP_RIGHT = 3
    BOTTOM_LEFT = 4
    BOTTOM_RIGHT = 5

class InfoBar:
    @staticmethod
    def success(
        title: str,
        content: str,
        duration: int = ...,
        position: InfoBarPosition = ...,
        parent: QWidget | None = ...,
    ) -> None: ...
    @staticmethod
    def error(
        title: str,
        content: str,
        duration: int = ...,
        position: InfoBarPosition = ...,
        parent: QWidget | None = ...,
    ) -> None: ...

class NavigationInterface(QWidget):
    displayModeChanged: pyqtSignal
    def __init__(self, parent: QWidget | None = None) -> None: ...
    def addItem(
        self,
        routeKey: str,
        icon: Union[str, QIcon, FluentIconBase],
        text: str,
        onClick: Callable[[], None] | None = None,
        selectable: bool = True,
        position: NavigationItemPosition = NavigationItemPosition.TOP,
        tooltip: str | None = None,
        parentRouteKey: str | None = None,
    ) -> NavigationTreeWidget | None: ...
    def addWidget(
        self,
        routeKey: str,
        widget: NavigationWidget,
        onClick: Callable[[], None] | None = None,
        position: NavigationItemPosition = NavigationItemPosition.TOP,
        tooltip: str | None = None,
        parentRouteKey: str | None = None,
    ) -> None: ...
    def insertItem(
        self,
        index: int,
        routeKey: str,
        icon: Union[str, QIcon, FluentIconBase],
        text: str,
        onClick: Callable[[], None] | None = None,
        selectable: bool = True,
        position: NavigationItemPosition = NavigationItemPosition.TOP,
        tooltip: str | None = None,
        parentRouteKey: str | None = None,
    ) -> NavigationTreeWidget | None: ...
    def insertWidget(
        self,
        index: int,
        routeKey: str,
        widget: NavigationWidget,
        onClick: Callable[[], None] | None = None,
        position: NavigationItemPosition = NavigationItemPosition.TOP,
        tooltip: str | None = None,
        parentRouteKey: str | None = None,
    ) -> None: ...
    def setCurrentItem(self, routeKey: str) -> None: ...
    def removeWidget(self, routeKey: str) -> None: ...
    def addSeparator(
        self, position: NavigationItemPosition = NavigationItemPosition.TOP
    ) -> None: ...

class FluentStyleSheet(Enum):
    FLUENT_WINDOW: FluentStyleSheet
    NAVIGATION_INTERFACE: FluentStyleSheet
    def apply(self, widget: QWidget) -> None: ...

class FluentTitleBar(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None: ...

class SplashScreen(QWidget):
    def __init__(self, icon: QIcon | None = None, parent: QWidget | None = None) -> None: ...
    def setIconSize(self, size: Any) -> None: ...
    def finish(self) -> None: ...

class SwitchButton(QPushButton):
    checkedChanged: pyqtSignal
    def __init__(self, parent: QWidget | None = None, indicatorPos: Any = ...) -> None: ...

class _Router(QWidget):
    emptyChanged: pyqtSignal
    def setDefaultRouteKey(self, widget: Any, key: str) -> None: ...
    def pop(self) -> None: ...
    def remove(self, key: str) -> None: ...

qrouter: _Router

def isDarkTheme() -> bool: ...
def setTheme(theme: Theme, save: bool = False, lazy: bool = False) -> None: ...
def setThemeColor(color: QColor | Qt.GlobalColor | str, save: bool = False) -> None: ...
