import os.path

from PyQt5.QtCore import QSize
from PyQt5.QtGui import QColor, QIcon
from qfluentwidgets import (
    FluentIcon,
    SplashScreen,
)

from src.bot import Bot
from src.const import RESOURCE_FOLDER
from src.gui.account_frame import AccountFrame
from src.gui.components.no_animated_fluent_window import NoAnimatedFluentWindow
from src.gui.consts import BASE_HEIGHT, BASE_WIDTH
from src.signals.shared_farm_signals import SharedSignals


class MainWindow(NoAnimatedFluentWindow):
    def __init__(
        self,
        title: str,
        shared_signals: SharedSignals,
        *args,
        **kwargs,
    ) -> None:
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
        bots = list(account_by_id.values())
        for account_id, account in account_by_id.items():
            self.add_account(account_id, account, bots)

    def add_account(self, account_id: int, account: Bot, bots: list[Bot]):
        login = account.account["apikey"]["login"]
        account_widget = AccountFrame(
            login,
            account_id,
            account.logger,
            account.msg_info_signals,
            account.game_info_signals,
            account.bot_signals,
            account.grid_signals,
            account.world_signals,
            account.log_signals,
            bots,
        )
        navigation_widget = self.addSubInterface(
            account_widget, self.disconnected_icon, login
        )
        account.game_info_signals.is_ready_to_play.connect(
            lambda: navigation_widget.setIcon(self.connected_icon)
        )
        account.game_info_signals.disconnected.connect(
            lambda: navigation_widget.setIcon(self.disconnected_icon)
        )

    def closeEvent(self, e):
        self.shared_signals.closed.emit()
        return super().closeEvent(e)
