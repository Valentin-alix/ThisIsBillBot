from qfluentwidgets import FluentIcon, FluentWindow

from src.gui.account_widget import AccountWidget
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

        self.init_window()

        for account in account_by_id.values():
            self.add_account(account)

    def init_window(self):
        self.setWindowTitle(self.title)
        self.resize(BASE_WIDTH, BASE_HEIGHT)

    def add_account(self, account: Bot):
        bot = AccountWidget(account)
        self.addSubInterface(bot, FluentIcon.PEOPLE, account.account_nickname)
