import ctypes

from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QApplication, QWidget

from src.gui.consts import BASE_HEIGHT, BASE_WIDTH
from src.gui.startup_splash_screen import StartupSplashScreen
from src.utils.project_paths import BUNDLE_ROOT


class Application(QApplication):
    TITLE = "Bill"

    def __init__(self, argv: list[str]) -> None:
        super().__init__(argv)
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(self.TITLE)
        self.setWindowIcon(QIcon(str(BUNDLE_ROOT / "resources/icons/logo.png")))
        self.setApplicationName(self.TITLE)
        self.startup_window = QWidget()
        self.startup_window.setWindowTitle(self.TITLE)
        self.startup_window.setWindowIcon(self.windowIcon())
        self.startup_window.setWindowFlag(Qt.WindowType.WindowCloseButtonHint, False)
        self.startup_window.resize(BASE_WIDTH, BASE_HEIGHT)
        self.startup_splash = StartupSplashScreen(self.windowIcon(), self.startup_window)
        self.startup_splash.setIconSize(QSize(102, 102))

    def show_startup_status(self, status: str) -> None:
        self.startup_splash.set_status(status)
        self.startup_window.show()
        self.processEvents()
