import ctypes
import sys

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

from src.const import LOGO_FILE


class Application(QApplication):
    TITLE = "Bot Dofus 3"

    def __init__(self, argv: list[str]) -> None:
        super().__init__(argv)
        if sys.platform == "win32":
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(self.TITLE)
        self.setWindowIcon(QIcon(LOGO_FILE))
        self.setApplicationName(self.TITLE)
