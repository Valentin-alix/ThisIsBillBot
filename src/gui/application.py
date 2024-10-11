import ctypes
import os

from PyQt5.QtCore import (
    Qt,
)
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QApplication,
)

from src.const import RESOURCE_FOLDER


class Application(QApplication):
    TITLE = "Bot Dofus 3"

    def __init__(self, argv: list[str]) -> None:
        super().__init__(argv)
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(self.TITLE)
        self.setWindowIcon(QIcon(os.path.join(RESOURCE_FOLDER, "logo.png")))
        self.setAttribute(Qt.ApplicationAttribute.AA_DisableWindowContextHelpButton)
        self.setApplicationName(self.TITLE)
