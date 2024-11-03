import os
import sys
from pathlib import Path
from threading import Thread

from dotenv import load_dotenv
from PyQt5.QtCore import Qt
from qfluentwidgets import Theme, setTheme, setThemeColor

load_dotenv()

sys.path.append(os.path.join(Path(__file__).parent))
sys.path.append(os.path.join(Path(__file__).parent, "D3Mapping"))
sys.path.append(os.path.join(Path(__file__).parent, "DBDofusUnity"))
sys.path.append(os.path.join(Path(__file__).parent, "D3Database"))


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

from src.bot_manager import BotManager  # noqa: E402
from src.const import DOFUS_CONNECTION_URL  # noqa: E402
from src.gui.application import Application  # noqa: E402
from src.gui.main_window import MainWindow  # noqa: E402
from src.mitm.proxy_listener import ProxyListener  # noqa: E402
from src.scheduler import run_continuously  # noqa: E402
from src.signals.shared_farm_signals import SharedSignals  # noqa: E402


def main() -> None:
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
