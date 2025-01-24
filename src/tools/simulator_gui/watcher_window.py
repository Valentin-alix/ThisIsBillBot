import importlib
import os
import sys
from dataclasses import dataclass, field
from types import ModuleType

from dotenv import load_dotenv
from PyQt6.QtCore import QObject, Qt, pyqtSignal
from PyQt6.QtWidgets import QApplication
from qfluentwidgets import Theme, setTheme, setThemeColor
from watchfiles import Change, watch

from src.const import ENV_PATH
from src.core.bot.bot import Bot
from src.core.bot.bot_factory import generate_random_bot

load_dotenv(ENV_PATH)

import src.core.signals.shared_farm_signals as gui_shared_farm_signals
import src.gui.main_window as gui_main_window
from src.gui.application import Application
from src.gui.main_window import MainWindow


class ReloadSignaler(QObject):
    reload_requested = pyqtSignal()


@dataclass
class WatcherGui:
    app: Application = field(init=False)
    shared_signals: gui_shared_farm_signals.SharedSignals = field(init=False)
    main_window: MainWindow = field(init=False)
    fake_bots: list[Bot] = field(init=False)
    reload_signaler: ReloadSignaler = field(init=False, default_factory=ReloadSignaler)

    def __post_init__(self) -> None:
        self.app = Application(sys.argv)
        self.shared_signals = gui_shared_farm_signals.SharedSignals()
        self.main_window = gui_main_window.MainWindow(
            title=self.app.TITLE, shared_signals=self.shared_signals
        )
        self.main_window.show()
        setTheme(Theme.DARK)
        setThemeColor(Qt.GlobalColor.yellow)
        fake_bots: list[Bot] = [generate_random_bot() for _ in range(1)]
        self.fake_bots = fake_bots
        self.populate_window(self.main_window)
        self.reload_signaler.reload_requested.connect(self.reload_ui)

    def watch_filter(self, _: Change, filename: str) -> bool:
        if not filename.endswith(".py"):
            return False

        norm = os.path.normpath(filename).replace("\\", "/")
        patterns = ["src/gui"]
        return any(p in norm for p in patterns)

    def watch_files(self) -> None:
        for _ in watch("./", watch_filter=self.watch_filter):
            print("Changement détecté, rechargement…")
            self.reload_signaler.reload_requested.emit()

    def reload_ui(self) -> None:
        global gui_main_window
        print("reload_ui called")

        fake_bots: list[Bot] = [generate_random_bot() for _ in range(1)]
        self.fake_bots = fake_bots

        prev_geom = None
        was_maximized = False
        if self.main_window is not None:
            prev_geom = self.main_window.saveGeometry()
            was_maximized = self.main_window.isMaximized()

        gui_path_patterns = [os.path.normpath(os.path.join("src", "gui"))]

        purge_names: list[str] = []
        for name, mod in list(sys.modules.items()):
            if name.startswith("src.gui"):
                purge_names.append(name)
                continue
            try:
                mod_file = mod.__file__ if isinstance(mod, ModuleType) else None
            except AttributeError:
                continue
            if not mod_file:
                continue
            norm = os.path.normpath(mod_file)
            if any(p in norm for p in gui_path_patterns):
                purge_names.append(name)

        for name in purge_names:
            del sys.modules[name]

        gui_main_window = importlib.import_module("src.gui.main_window")
        new_window = gui_main_window.MainWindow(
            title=self.app.TITLE, shared_signals=self.shared_signals
        )
        if prev_geom is not None:
            new_window.restoreGeometry(prev_geom)

        if was_maximized:
            new_window.showMaximized()
        else:
            new_window.show()

        new_window.raise_()
        new_window.activateWindow()
        new_window.setFocus()
        QApplication.setActiveWindow(new_window)

        QApplication.processEvents()

        if self.main_window is not None:
            self.main_window.close()
            self.main_window.deleteLater()
            QApplication.processEvents()

        self.main_window = new_window
        self.populate_window(new_window)
        QApplication.processEvents()

    def populate_window(self, win: MainWindow) -> None:
        for fake_bot in self.fake_bots:
            win.add_account(fake_bot)
        win.splashScreen.finish()
