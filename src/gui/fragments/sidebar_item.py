import os

from PyQt5.QtCore import QMargins, QPoint, QRect, Qt, pyqtSignal
from PyQt5.QtGui import QColor, QCursor, QIcon, QPainter
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QSizePolicy, QSpacerItem
from qfluentwidgets import (
    BodyLabel,
    ComboBox,
    FluentIcon,
    TransparentToolButton,
)
from qfluentwidgets.common.config import isDarkTheme
from qfluentwidgets.common.icon import toQIcon
from qfluentwidgets.common.style_sheet import themeColor
from qfluentwidgets.components.navigation.navigation_widget import NavigationWidget

from src.const import RESOURCE_FOLDER
from src.core.signals.bot_signals import BotSignals


class SidebarItem(NavigationWidget):
    network_interface_changed = pyqtSignal(str)
    schedule_profile_changed = pyqtSignal(str)
    play_clicked = pyqtSignal()
    stop_clicked = pyqtSignal()

    def __init__(
        self,
        bot_signals: BotSignals,
        left_icon: FluentIcon | QIcon,
        title: str,
        isSelectable: bool,
        parent=None,
    ):
        super().__init__(
            isSelectable=isSelectable,
            parent=parent,
        )
        self.bot_signals = bot_signals
        self.in_fight: bool = False
        self._is_playing: bool = False
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

        self._play_btn = TransparentToolButton(FluentIcon.PLAY)
        self._play_btn.setFixedSize(24, 24)
        self._play_btn.clicked.connect(self.on_click_play)
        self.bot_signals.play.connect(self.on_play)
        self.layout().addWidget(self._play_btn)

        self._stop_btn = TransparentToolButton(FluentIcon.PAUSE)
        self._stop_btn.setFixedSize(24, 24)
        self._stop_btn.clicked.connect(self.on_click_stop)
        self.bot_signals.stop.connect(self.on_stop)
        self._stop_btn.hide()
        self.layout().addWidget(self._stop_btn)

        self._profile_combo = ComboBox()
        self._profile_combo.setFixedWidth(60)
        self._profile_combo.currentIndexChanged.connect(self._on_profile_changed)
        self.layout().addWidget(self._profile_combo)

        self._network_combo = ComboBox()
        self._network_combo.setFixedWidth(60)
        self._network_combo.currentIndexChanged.connect(
            self._on_network_interface_changed
        )
        self.layout().addWidget(self._network_combo)

    def show_battle_icon(self, show: bool):
        self.in_fight = show
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
            self.setFixedSize(40, 48)
            self._title.hide()
            self._right_icon.hide()
            self._play_btn.hide()
            self._stop_btn.hide()
            self._profile_combo.hide()
            self._network_combo.hide()
        else:
            self.setFixedSize(self.EXPAND_WIDTH, 48)
            self._title.show()
            if self.in_fight:
                self._right_icon.show()
            if self._is_playing:
                self._stop_btn.show()
            else:
                self._play_btn.show()
            self._profile_combo.show()
            self._network_combo.show()

        self.update()

    def _margins(self):
        return QMargins(0, 0, 0, 0)

    def _canDrawIndicator(self):
        return self.isSelected

    def set_left_icon(self, icon: QIcon | FluentIcon):
        self._left_icon.setPixmap(toQIcon(icon).pixmap(16))

    def set_title(self, text: str):
        self._title.setText(text)

    def populate_network_interfaces(
        self, interfaces: dict[str, str], selected_ip: str | None
    ):
        self._network_combo.blockSignals(True)
        self._network_combo.clear()
        self._network_combo.addItem("Auto", userData=None)
        for name, ip in interfaces.items():
            self._network_combo.addItem(name, userData=ip)
        if selected_ip:
            for i in range(self._network_combo.count()):
                if self._network_combo.itemData(i) == selected_ip:
                    self._network_combo.setCurrentIndex(i)
                    break
        else:
            self._network_combo.setCurrentIndex(0)
        self._network_combo.blockSignals(False)

    def populate_schedule_profiles(
        self, profiles: dict[str, str], selected_profile: str | None
    ):
        self._profile_combo.blockSignals(True)
        self._profile_combo.clear()
        self._profile_combo.addItem("Vide", userData=None)
        for profile_id, display_name in profiles.items():
            self._profile_combo.addItem(display_name, userData=profile_id)
        if selected_profile:
            for i in range(self._profile_combo.count()):
                if self._profile_combo.itemData(i) == selected_profile:
                    self._profile_combo.setCurrentIndex(i)
                    break
        else:
            self._profile_combo.setCurrentIndex(0)
        self._profile_combo.blockSignals(False)

    def _on_profile_changed(self):
        profile_id = self._profile_combo.currentData()
        self.schedule_profile_changed.emit(profile_id if profile_id else "")

    def _on_network_interface_changed(self):
        ip = self._network_combo.currentData()
        self.network_interface_changed.emit(ip if ip else "")

    def on_click_play(self):
        self.bot_signals.play.emit(True)
        self.bot_signals.play_auto_bot.emit()

    def on_click_stop(self):
        self.bot_signals.stop.emit()

    def on_play(self, _):
        self._is_playing = True
        self._stop_btn.show()
        self._play_btn.hide()

    def on_stop(self):
        self._is_playing = False
        self._play_btn.show()
        self._stop_btn.hide()

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
