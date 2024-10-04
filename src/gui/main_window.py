from PyQt5.QtGui import QColor
from qfluentwidgets import FluentIcon, FluentWindow

from src.gui.components.account_widget import AccountWidget
from src.gui.consts import BASE_HEIGHT, BASE_WIDTH
from src.interfaces.models.bot import Bot


class MainWindow(FluentWindow):
    def __init__(
        self,
        account_by_id: dict[int, Bot],
        title: str,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.title = title

        self.disconnected_icon = FluentIcon.PEOPLE.icon(color=QColor(255, 0, 0))
        self.connected_icon = FluentIcon.PEOPLE.icon(color=QColor(0, 255, 0))

        self.init_window()

        for account in account_by_id.values():
            self.add_account(account)

    def init_window(self):
        self.setWindowTitle(self.title)
        self.resize(BASE_WIDTH, BASE_HEIGHT)

    def add_account(self, account: Bot):
        login = account.account["apikey"]["login"]
        account_widget = AccountWidget(
            login,
            account.msg_info_signals,
            account.player_property_signals,
            account.harvester_signals,
        )
        navigation_widget = self.addSubInterface(
            account_widget, self.disconnected_icon, login
        )
        account.player_signals.connected.connect(
            lambda: navigation_widget.setIcon(self.connected_icon)
        )
        account.player_signals.disconnected.connect(
            lambda: navigation_widget.setIcon(self.disconnected_icon)
        )
