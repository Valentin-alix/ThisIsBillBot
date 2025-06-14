import os

from PyQt6.QtCore import QMargins, QPoint, QRect, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QCursor, QIcon, QPainter, QPaintEvent
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)
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

NO_SCHEDULE_PROFILE_ID = ""
NO_SCHEDULE_PROFILE_LABEL = "Aucun profil"


class SidebarItem(NavigationWidget):
    schedule_profile_changed = pyqtSignal(str)
    connection_mode_changed = pyqtSignal(str)
    play_clicked = pyqtSignal()
    stop_clicked = pyqtSignal()

    def __init__(
        self,
        bot_signals: BotSignals,
        left_icon: FluentIcon | QIcon,
        title: str,
        isSelectable: bool,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(
            isSelectable=isSelectable,
            parent=parent,
        )
        self.bot_signals = bot_signals
        self.in_fight: bool = False
        self._is_playing: bool = False
        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.header_layout = QHBoxLayout()
        self.header_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.header_layout.setContentsMargins(4, 0, 12, 0)

        self.controls_layout = QHBoxLayout()
        self.controls_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.setLayout(self.main_layout)
        self.main_layout.addLayout(self.header_layout)
        self.main_layout.addLayout(self.controls_layout)

        self._left_icon = QLabel(self)
        self._left_icon.setPixmap(toQIcon(left_icon).pixmap(16))
        self.header_layout.addWidget(self._left_icon)

        self._title = BodyLabel(title, self)
        self.header_layout.addWidget(self._title)

        spacer = QSpacerItem(
            0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )
        self.header_layout.addItem(spacer)

        self._right_icon = QLabel(self)
        battle_icon = QIcon(os.path.join(RESOURCE_FOLDER, "icons", "combat.png"))
        self._right_icon.setPixmap(battle_icon.pixmap(16))
        self._right_icon.hide()
        self.header_layout.addWidget(self._right_icon)

        self._play_btn = TransparentToolButton(FluentIcon.PLAY, self)
        self._play_btn.setFixedSize(24, 24)
        self._play_btn.clicked.connect(self.on_click_play)
        self.bot_signals.play.connect(self.on_play)
        self.header_layout.addWidget(self._play_btn)

        self._stop_btn = TransparentToolButton(FluentIcon.PAUSE, self)
        self._stop_btn.setFixedSize(24, 24)
        self._stop_btn.clicked.connect(self.on_click_stop)
        self.bot_signals.stop.connect(self.on_stop)
        self._stop_btn.hide()
        self.header_layout.addWidget(self._stop_btn)

        self._profile_combo = ComboBox(self)
        self._profile_combo.setFixedWidth(150)
        self._profile_combo.currentIndexChanged.connect(self._on_profile_changed)
        self.controls_layout.addWidget(self._profile_combo)

        self._mode_combo = ComboBox(self)
        self._mode_combo.setFixedWidth(150)
        self._mode_combo.addItem("Mitm", userData="mitm")
        self._mode_combo.addItem("Socket", userData="socket")
        self._mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        self.controls_layout.addWidget(self._mode_combo)

    def show_battle_icon(self, show: bool) -> None:
        self.in_fight = show
        if show:
            self._right_icon.show()
        else:
            self._right_icon.hide()

    def setCompacted(self, isCompacted: bool) -> None:
        """set whether the widget is compacted"""
        if isCompacted == self.isCompacted:
            return

        self.isCompacted = isCompacted
        if isCompacted:
            self.header_layout.setContentsMargins(0, 0, 0, 0)
            self.setFixedSize(40, 48)
            self._title.hide()
            self._right_icon.hide()
            self._play_btn.hide()
            self._stop_btn.hide()
            self._profile_combo.hide()
            self._mode_combo.hide()
        else:
            self.header_layout.setContentsMargins(4, 0, 12, 0)
            self.setFixedSize(self.EXPAND_WIDTH, 96)
            self._title.show()
            if self.in_fight:
                self._right_icon.show()
            if self._is_playing:
                self._stop_btn.show()
            else:
                self._play_btn.show()
            self._profile_combo.show()
            self._mode_combo.show()

        self.update()

    def _margins(self) -> QMargins:
        return QMargins(0, 0, 0, 0)

    def _canDrawIndicator(self) -> bool:
        return self.isSelected

    def set_left_icon(self, icon: QIcon | FluentIcon) -> None:
        self._left_icon.setPixmap(toQIcon(icon).pixmap(16))

    def set_title(self, text: str) -> None:
        self._title.setText(text)

    def populate_schedule_profiles(
        self, profiles: dict[str, str], selected_profile: str | None
    ) -> None:
        self._profile_combo.blockSignals(True)
        self._profile_combo.clear()
        self._profile_combo.addItem(
            NO_SCHEDULE_PROFILE_LABEL, userData=NO_SCHEDULE_PROFILE_ID
        )
        for profile_id, display_name in profiles.items():
            self._profile_combo.addItem(display_name, userData=profile_id)
        selected_data = selected_profile or NO_SCHEDULE_PROFILE_ID
        selected_index = self._profile_combo.findData(selected_data)
        assert selected_index >= 0, f"Unknown schedule profile {selected_profile}"
        self._profile_combo.setCurrentIndex(selected_index)
        self._profile_combo.blockSignals(False)

    def _on_profile_changed(self) -> None:
        profile_id = self._profile_combo.currentData()
        has_schedule_profile = isinstance(profile_id, str) and profile_id != ""
        self.schedule_profile_changed.emit(profile_id if has_schedule_profile else "")

    def populate_connection_mode(self, selected_mode: str) -> None:
        for mode_index in range(self._mode_combo.count()):
            if self._mode_combo.itemData(mode_index) == selected_mode:
                self._mode_combo.setCurrentIndex(mode_index)
                return

    def _on_mode_changed(self) -> None:
        mode = self._mode_combo.currentData()
        self.connection_mode_changed.emit(mode if mode else "mitm")

    def on_click_play(self) -> None:
        self.bot_signals.play.emit(True)
        self.bot_signals.play_auto_bot.emit()

    def on_click_stop(self) -> None:
        self.bot_signals.stop.emit()

    def on_play(self, _: bool) -> None:
        self._is_playing = True
        self._stop_btn.show()
        self._play_btn.hide()

    def on_stop(self) -> None:
        self._is_playing = False
        self._play_btn.show()
        self._stop_btn.hide()

    def paintEvent(self, a0: QPaintEvent | None) -> None:
        painter = QPainter(self)
        painter.setRenderHints(
            QPainter.RenderHint.Antialiasing
            | QPainter.RenderHint.TextAntialiasing
            | QPainter.RenderHint.SmoothPixmapTransform
        )
        painter.setPen(Qt.PenStyle.NoPen)

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
            indicator_height = max(16, int(self.height() * 0.65))
            indicator_top = (self.height() - indicator_height) // 2
            painter.drawRoundedRect(pl, indicator_top, 3, indicator_height, 1.5, 1.5)
        elif self.isEnter and self.isEnabled() and globalRect.contains(QCursor.pos()):
            painter.setBrush(QColor(c, c, c, 10))
            painter.drawRoundedRect(self.rect(), 5, 5)

        painter.setFont(self.font())
        painter.setPen(self.textColor())
