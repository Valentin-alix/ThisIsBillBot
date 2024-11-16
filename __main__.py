import os
import sys
from threading import Thread
from time import sleep

from dotenv import load_dotenv
from PyQt5.QtCore import Qt
from qfluentwidgets import Theme, setTheme, setThemeColor

from src.utils.internet import has_internet_connection

while not has_internet_connection():
    print("waiting for internet connection")
    sleep(1)

load_dotenv()


if hasattr(sys, "_MEIPASS"):
    base_path = sys._MEIPASS  # type: ignore
    sys.path.append(
        os.path.join(
            base_path, "D3Mapping", "d3_mapping", "resources", "protos", "game"
        )
    )
    sys.path.append(
        os.path.join(
            base_path, "D3Mapping", "d3_mapping", "resources", "protos", "connection"
        )
    )

from src.const import DOFUS_CONNECTION_URL  # noqa: E402
from src.core.bot.bot_manager import BotManager  # noqa: E402
from src.core.bot.lifecycle.scheduler import run_continuously  # noqa: E402
from src.core.mitm.proxy_listener import ProxyListener  # noqa: E402
from src.core.signals.shared_farm_signals import SharedSignals  # noqa: E402
from src.gui.application import Application  # noqa: E402
from src.gui.main_window import MainWindow  # noqa: E402


def main() -> None:
    # reflechir a d'autre idée pour aller plus vite dans le mapping
    # -> pouvoir après avoir sniffer et rec les datas lancer le mapping et savoir quel champs est problématique ou non -> utiliser pydantic pour full valider des champs ?
    app = Application(sys.argv)
    shared_signals = SharedSignals()
    main_window = MainWindow(title=app.TITLE, shared_signals=shared_signals)
    main_window.show()
    setTheme(Theme.DARK)
    setThemeColor(Qt.GlobalColor.yellow)

    bot_manager = BotManager(shared_signals=shared_signals)
    listener = ProxyListener(account_by_id=bot_manager.bot_by_account_id)
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
        bot.start()

    cease_running = run_continuously()
    shared_signals.closed.connect(cease_running.set)

    app.exec()


if __name__ == "__main__":
    main()
    # profiler = cProfile.Profile()
    # profiler.enable()

    # exit_code = main()

    # profiler.disable()
    # profiler.dump_stats(os.path.join(RESOURCE_FOLDER, "profile.prof"))
