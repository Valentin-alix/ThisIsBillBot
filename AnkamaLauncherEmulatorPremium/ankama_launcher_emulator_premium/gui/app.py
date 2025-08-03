import sys

from PyQt6.QtWidgets import (
    QApplication,
)
from qfluentwidgets import (
    Theme,
    setTheme,
)

from ankama_launcher_emulator_premium.decrypter.crypto_helper import CryptoHelper
from ankama_launcher_emulator_premium.gui.windows.main_window import MainWindow
from ankama_launcher_emulator_premium.server.handler import AnkamaLauncherHandler
from ankama_launcher_emulator_premium.server.server import AnkamaLauncherServer


def run_gui() -> None:
    handler = AnkamaLauncherHandler()
    server = AnkamaLauncherServer(handler)
    server.start()

    accounts = CryptoHelper.getStoredApiKeys()

    app = QApplication(sys.argv)
    setTheme(Theme.DARK)

    window = MainWindow(server, accounts)
    window.show()
    sys.exit(app.exec())
