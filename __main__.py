import logging
import os
import sys
from threading import Thread
from time import sleep

from dotenv import load_dotenv
from PyQt5.QtCore import Qt
from qfluentwidgets import Theme, setTheme, setThemeColor

from src.services.logging.logger import init_global_logging
from src.tools.lower_config import set_low_config_for_all
from src.utils.internet import has_internet_connection

logger = logging.getLogger()

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

init_global_logging()


def main() -> None:
    set_low_config_for_all()
    app = Application(sys.argv)
    shared_signals = SharedSignals()
    main_window = MainWindow(title=app.TITLE, shared_signals=shared_signals)
    main_window.show()
    setTheme(Theme.DARK)
    setThemeColor(Qt.GlobalColor.yellow)

    bot_manager = BotManager(shared_signals=shared_signals)
    proxy_listener = ProxyListener(account_by_id=bot_manager.bot_by_account_id)
    proxy_dofus = proxy_listener.create_server(5555)
    Thread(
        target=lambda: proxy_listener.start_listener(
            proxy_dofus, (DOFUS_CONNECTION_URL, 5555), True
        ),
        daemon=True,
    ).start()
    main_window.init_accounts(bot_manager.bot_by_account_id)
    main_window.splashScreen.finish()

    for bot in bot_manager.bot_by_account_id.values():
        bot.start()

    cease_running = run_continuously()

    def on_app_close():
        cease_running.set()
        proxy_listener.shutdown()
        bot_manager.shutdown()

    shared_signals.closed.connect(on_app_close)

    app.exec()


if __name__ == "__main__":
    main()
    # profiler = cProfile.Profile()
    # profiler.enable()

    # exit_code = main()

    # profiler.disable()
    # profiler.dump_stats(os.path.join(RESOURCE_FOLDER, "profile.prof"))
