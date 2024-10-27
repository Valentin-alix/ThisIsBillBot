import os

from PyQt5.QtCore import QMargins, QPoint, QRect, Qt
from PyQt5.QtGui import QColor, QCursor, QIcon, QPainter
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QSizePolicy, QSpacerItem
from qfluentwidgets import (
    BodyLabel,
    FluentIcon,
)
from qfluentwidgets.common.config import isDarkTheme
from qfluentwidgets.common.icon import toQIcon
from qfluentwidgets.common.style_sheet import themeColor
from qfluentwidgets.components.navigation.navigation_widget import NavigationWidget

from src.const import RESOURCE_FOLDER


class SidebarItem(NavigationWidget):
    def __init__(
        self, left_icon: FluentIcon | QIcon, title: str, isSelectable: bool, parent=None
    ):
        super().__init__(
            isSelectable=isSelectable,
            parent=parent,
        )
        self.main_layout = QHBoxLayout()
        self.main_layout.setAlignment(Qt.AlignLeft)
        self.setLayout(self.main_layout)

        self._left_icon = QLabel()
        self._left_icon.setPixmap(toQIcon(left_icon).pixmap(16))
        self.layout().addWidget(self._left_icon)

        self._title = BodyLabel(title)
        self.layout().addWidget(self._title)

        spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.layout().addItem(spacer)

        self._right_icon = QLabel()
        battle_icon = QIcon(os.path.join(RESOURCE_FOLDER, "icons", "combat.png"))
        self._right_icon.setPixmap(battle_icon.pixmap(16))
        self._right_icon.hide()
        self.layout().addWidget(self._right_icon)

    def show_battle_icon(self, show: bool):
        if show:
            self._right_icon.show()
        else:
            self._right_icon.hide()

    def setCompacted(self, isCompacted: bool):
        """set whether the widget is compacted"""
        if isCompacted == self.isCompacted:
            return

        self.isCompacted = isCompacted
        if isCompacted:
            self.setFixedSize(40, 36)
            self._title.hide()
        else:
            self.setFixedSize(self.EXPAND_WIDTH, 36)
            self._title.show()

        self.update()

    def _margins(self):
        return QMargins(0, 0, 0, 0)

    def _canDrawIndicator(self):
        return self.isSelected

    def set_left_icon(self, icon: QIcon | FluentIcon):
        self._left_icon.setPixmap(toQIcon(icon).pixmap(16))

    def set_title(self, text: str):
        self._title.setText(text)

    def paintEvent(self, a0):
        painter = QPainter(self)
        painter.setRenderHints(
            QPainter.Antialiasing
            | QPainter.TextAntialiasing
            | QPainter.SmoothPixmapTransform
        )
        painter.setPen(Qt.NoPen)

        if self.isPressed:
            painter.setOpacity(0.7)
        if not self.isEnabled():
            painter.setOpacity(0.4)

        # draw background
        c = 255 if isDarkTheme() else 0
        m = self._margins()
        pl = m.left()
        globalRect = QRect(self.mapToGlobal(QPoint()), self.size())

        if self._canDrawIndicator():
            painter.setBrush(QColor(c, c, c, 6 if self.isEnter else 10))
            painter.drawRoundedRect(self.rect(), 5, 5)

            # draw indicator
            painter.setBrush(themeColor())
            painter.drawRoundedRect(pl, 10, 3, 16, 1.5, 1.5)
        elif self.isEnter and self.isEnabled() and globalRect.contains(QCursor.pos()):
            painter.setBrush(QColor(c, c, c, 10))
            painter.drawRoundedRect(self.rect(), 5, 5)

        painter.setFont(self.font())
        painter.setPen(self.textColor())
