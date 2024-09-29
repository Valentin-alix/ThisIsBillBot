import sys
from pathlib import Path

from PyQt5.QtCore import (
    Qt,
)
from PyQt5.QtWidgets import (
    QApplication,
)
from qfluentwidgets import Theme, setTheme, setThemeColor

from src.interfaces.models.bot import Bot


sys.path.append(str(Path(__file__).parent.parent.parent))

from src.gui.main_window import MainWindow


class Application(QApplication):
    TITLE = "Dofus Unity"

    def __init__(self, argv: list[str]) -> None:
        super().__init__(argv)
        self.setAttribute(Qt.ApplicationAttribute.AA_DisableWindowContextHelpButton)
        self.setApplicationName(self.TITLE)


def launch_gui(account_by_id: dict[int, Bot]):
    app = Application(sys.argv)
    main_window = MainWindow(account_by_id, app.TITLE)
    main_window.show()
    setTheme(Theme.DARK)
    setThemeColor(Qt.GlobalColor.yellow)
    app.exec()
