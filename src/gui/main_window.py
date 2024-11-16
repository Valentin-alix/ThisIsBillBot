import os
import os.path

from PyQt5.QtCore import QSize
from PyQt5.QtGui import QColor, QIcon
from qfluentwidgets import FluentIcon, NavigationItemPosition, SplashScreen

from src.core.bot.bot import Bot
from src.const import RESOURCE_FOLDER
from src.core.signals.shared_farm_signals import SharedSignals
from src.gui.consts import BASE_HEIGHT, BASE_WIDTH
from src.gui.fragments.account_stacked_widget import AccountStackedWidget
from src.gui.fragments.app_fluent_window import AppFluentWindow
from src.gui.fragments.sidebar_item import SidebarItem


class MainWindow(AppFluentWindow):
    def __init__(self, title: str, shared_signals: SharedSignals) -> None:
        super().__init__(parent=None)

        self.title = title
        self.shared_signals = shared_signals
        self.setWindowTitle(self.title)
        self.resize(BASE_WIDTH, BASE_HEIGHT)
        self.setWindowIcon(QIcon(os.path.join(RESOURCE_FOLDER, "logo.png")))
        self.splashScreen = SplashScreen(self.windowIcon(), self)
        self.splashScreen.setIconSize(QSize(102, 102))

        self.disconnected_icon = FluentIcon.PEOPLE.icon(color=QColor(255, 0, 0))
        self.connected_icon = FluentIcon.PEOPLE.icon(color=QColor(0, 255, 0))

    def init_accounts(self, account_by_id: dict[int, Bot]):
        for account in account_by_id.values():
            self.add_account(account)

    def add_account(self, account: Bot):
        login = account.account["apikey"]["login"]

        account_widget = AccountStackedWidget(login, account)
        navigation_widget = SidebarItem(
            self.disconnected_icon, login, True, parent=self
        )
        account_widget.setObjectName(login)
        self.addWidget(
            account_widget,
            navigation_widget,
            position=NavigationItemPosition.SCROLL,
        )
        self.navigationInterface.panel.expand()

        account.game_info_signals.character_name.connect(navigation_widget.set_title)

        account.game_info_signals.in_fight.connect(navigation_widget.show_battle_icon)
        account.game_info_signals.is_ready_to_play.connect(
            lambda: navigation_widget.set_left_icon(self.connected_icon)
        )
        account.game_info_signals.disconnected.connect(
            lambda: navigation_widget.set_left_icon(self.disconnected_icon)
        )
        account.game_info_signals.disconnected.connect(
            lambda: navigation_widget.set_title(login)
        )

    def closeEvent(self, *args, **kwargs):
        self.shared_signals.closed.emit()
        return super().closeEvent(*args, **kwargs)
