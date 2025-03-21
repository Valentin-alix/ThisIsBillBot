import sys
from pathlib import Path
from time import sleep

from dotenv import load_dotenv
from PyQt6.QtCore import Qt
from qfluentwidgets import Theme, setTheme, setThemeColor

from src.services.logging_utils.loggers import configure_root_logger
from src.utils.runtime_paths import configure_project_import_paths

configure_project_import_paths(Path(__file__).resolve().parent)

from src.utils.internet import has_internet_connection

while not has_internet_connection():
    print("waiting for internet connection")
    sleep(1)

load_dotenv()

from src.core.bot.bot_manager import BotManager  # noqa: E402
from src.core.bot.lifecycle.scheduler import run_continuously  # noqa: E402
from src.core.signals.shared_farm_signals import SharedSignals  # noqa: E402
from src.gui.application import Application  # noqa: E402
from src.gui.main_window import MainWindow  # noqa: E402


def main() -> None:
    configure_root_logger()

    app = Application(sys.argv)
    shared_signals = SharedSignals()
    main_window = MainWindow(title=app.TITLE, shared_signals=shared_signals)
    main_window.show()
    setTheme(Theme.DARK)
    setThemeColor(Qt.GlobalColor.yellow)

    bot_manager = BotManager(shared_signals=shared_signals)

    bot_manager.ankama_launcher.start()
    main_window.init_accounts(bot_manager.bot_by_account_id)
    main_window.splashScreen.finish()

    for bot in bot_manager.bot_by_account_id.values():
        bot.start()

    cease_running = run_continuously()

    def on_app_close():
        cease_running.set()
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
