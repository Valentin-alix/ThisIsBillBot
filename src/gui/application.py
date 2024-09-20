import sys
from pathlib import Path

from PyQt5.QtCore import (
    Qt,
)
from PyQt5.QtWidgets import (
    QApplication,
)
from qfluentwidgets import Theme, setTheme, setThemeColor

sys.path.append(str(Path(__file__).parent.parent.parent))
from src.gui.main_window import MainWindow
from src.gui.signals.msg_signals import MessageSignals


class Application(QApplication):
    TITLE = "Dofus Unity"

    def __init__(self, argv: list[str]) -> None:
        super().__init__(argv)
        self.setAttribute(Qt.ApplicationAttribute.AA_DisableWindowContextHelpButton)
        self.setApplicationName(self.TITLE)


def launch_gui(msg_signals: MessageSignals):
    app = Application(sys.argv)
    main_window = MainWindow(msg_signals, app.TITLE)
    main_window.show()
    setTheme(Theme.LIGHT)
    setThemeColor(Qt.GlobalColor.yellow)
    app.exec()
