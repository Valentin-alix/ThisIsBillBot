import sys
from threading import Thread

from PyQt5.QtCore import Qt
from qfluentwidgets import Theme, setTheme, setThemeColor

from src.bot_manager import BotManager
from src.gui.application import Application
from src.gui.main_window import MainWindow
from src.mitm.proxy_listener import ProxyListener


def main() -> None:
    app = Application(sys.argv)
    main_window = MainWindow(app.TITLE)
    main_window.show()

    bot_manager = BotManager()
    listener = ProxyListener(bot_manager.bot_by_account_id)
    Thread(
        target=lambda: listener.start_listener(
            5555, ("dofus2-co-beta.ankama-games.com", 5555), True
        ),
        daemon=True,
    ).start()
    main_window.init_accounts(bot_manager.bot_by_account_id)
    main_window.splashScreen.finish()

    setTheme(Theme.DARK)
    setThemeColor(Qt.GlobalColor.yellow)
    app.exec()


if __name__ == "__main__":
    main()
