import os.path

from PyQt5.QtCore import QSize
from PyQt5.QtGui import QColor, QIcon
from qfluentwidgets import FluentIcon, FluentWindow, SplashScreen

from src.bot import Bot
from src.consts import RESOURCE_FOLDER
from src.gui.components.account_widget import AccountWidget
from src.gui.consts import BASE_HEIGHT, BASE_WIDTH


class MainWindow(FluentWindow):
    def __init__(
        self,
        title: str,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.title = title
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
        account_widget = AccountWidget(
            login,
            account.msg_info_signals,
            account.game_info_signals,
            account.harvester_signals,
            account.grid_signals,
        )
        navigation_widget = self.addSubInterface(
            account_widget, self.disconnected_icon, login
        )
        account.game_info_signals.connected.connect(
            lambda: navigation_widget.setIcon(self.connected_icon)
        )
        account.game_info_signals.disconnected.connect(
            lambda: navigation_widget.setIcon(self.disconnected_icon)
        )
