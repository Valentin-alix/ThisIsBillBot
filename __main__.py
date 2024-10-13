import os.path
import sys
from pathlib import Path
from threading import Thread

from PyQt5.QtCore import Qt
from qfluentwidgets import Theme, setTheme, setThemeColor

sys.path.append(os.path.join(Path(__file__).parent, "D3Database"))

from src.const import DOFUS_CONNECTION_URL
from src.mitm.proxy_listener import ProxyListener
from src.signals.shared_farm_signals import SharedSignals
from src.signals.shared_subjects import SharedSubjects
from src.bot_manager import BotManager
from src.gui.application import Application
from src.gui.main_window import MainWindow


def main() -> None:
    app = Application(sys.argv)
    shared_signals = SharedSignals()
    main_window = MainWindow(app.TITLE, shared_signals)
    main_window.show()
    setTheme(Theme.DARK)
    setThemeColor(Qt.GlobalColor.yellow)

    shared_subjects = SharedSubjects()
    bot_manager = BotManager(
        shared_signals=shared_signals, shared_subjects=shared_subjects
    )
    listener = ProxyListener(bot_manager.bot_by_account_id)
    Thread(
        target=lambda: listener.start_listener(
            5555, (DOFUS_CONNECTION_URL, 5555), True
        ),
        daemon=True,
    ).start()
    main_window.init_accounts(bot_manager.bot_by_account_id)
    main_window.splashScreen.finish()

    for bot in bot_manager.bot_by_account_id.values():
        if bot.account["apikey"]["login"] == "ezrealeu44700_1@outlook.com":
            bot.bot_signals.play_harvester.emit(8, None)
        elif bot.account["apikey"]["login"] == "ezrealeu44700_2@outlook.com":
            bot.bot_signals.play_harvester.emit(48, None)
        elif bot.account["apikey"]["login"] == "ezrealeu44700_3@outlook.com":
            bot.bot_signals.play_harvester.emit(46, None)
        elif bot.account["apikey"]["login"] == "ezrealeu44700_4@outlook.com":
            bot.bot_signals.play_harvester.emit(78, None)
        elif bot.account["apikey"]["login"] == "ezrealeu44700_1+s1@outlook.com":
            bot.bot_signals.play_harvester.emit(28, None)
        elif bot.account["apikey"]["login"] == "ezrealeu44700_1+s2@outlook.com":
            bot.bot_signals.play_harvester.emit(0, None)

    app.exec()


if __name__ == "__main__":
    main()
