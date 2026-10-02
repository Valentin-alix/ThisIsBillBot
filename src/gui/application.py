import ctypes

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

from src.consts import LOGO_FILE


class Application(QApplication):
    TITLE = "Bill"

    def __init__(self, argv: list[str]) -> None:
        super().__init__(argv)
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(self.TITLE)
        self.setWindowIcon(QIcon(LOGO_FILE))
        self.setApplicationName(self.TITLE)
