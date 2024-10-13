import os.path
import sys
from pathlib import Path
from threading import Thread

from PyQt5.QtCore import Qt
from qfluentwidgets import Theme, setTheme, setThemeColor

sys.path.append(os.path.join(Path(__file__).parent, "D3Mapping"))
sys.path.append(os.path.join(Path(__file__).parent, "D3Database"))

from src.bot_manager import BotManager
from src.const import DOFUS_CONNECTION_URL
from src.gui.application import Application
from src.gui.main_window import MainWindow
from src.mitm.proxy_listener import ProxyListener
from src.signals.shared_farm_signals import SharedSignals


def main() -> None:
    app = Application(sys.argv)
    shared_signals = SharedSignals()
    main_window = MainWindow(app.TITLE)
    main_window.show()
    setTheme(Theme.DARK)
    setThemeColor(Qt.GlobalColor.yellow)

    bot_manager = BotManager(shared_signals=shared_signals)
    listener = ProxyListener(bot_manager.bot_by_account_id)
    proxy_dofus = listener.create_server(5555)
    Thread(
        target=lambda: listener.start_listener(
            proxy_dofus, (DOFUS_CONNECTION_URL, 5555), True
        ),
        daemon=True,
    ).start()
    main_window.init_accounts(bot_manager.bot_by_account_id)
    main_window.splashScreen.finish()

    for bot in bot_manager.bot_by_account_id.values():
        ...
        # if bot.account["apikey"]["login"] == "ezrealeu44700_1@outlook.com":
        #     bot.bot_signals.play_harvester.emit(8, None)
        # elif bot.account["apikey"]["login"] == "ezrealeu44700_2@outlook.com":
        #     bot.bot_signals.play_harvester.emit(48, None)
        # elif bot.account["apikey"]["login"] == "ezrealeu44700_3@outlook.com":
        #     bot.bot_signals.play_harvester.emit(46, None)
        # elif bot.account["apikey"]["login"] == "ezrealeu44700_4@outlook.com":
        #     bot.bot_signals.play_harvester.emit(78, None)
        # elif bot.account["apikey"]["login"] == "ezrealeu44700_1+s1@outlook.com":
        #     bot.bot_signals.play_harvester.emit(28, None)
        # elif bot.account["apikey"]["login"] == "ezrealeu44700_1+s2@outlook.com":
        #     bot.bot_signals.play_harvester.emit(0, None)

    app.exec()


if __name__ == "__main__":
    main()
