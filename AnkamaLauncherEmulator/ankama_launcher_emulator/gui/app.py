import sys

from PyQt6.QtWidgets import (
    QApplication,
)
from qfluentwidgets import (
    Theme,
    setTheme,
)

from ankama_launcher_emulator.decrypter.crypto_helper import CryptoHelper
from ankama_launcher_emulator.gui.main_window import MainWindow
from ankama_launcher_emulator.server.handler import AnkamaLauncherHandler
from ankama_launcher_emulator.server.server import AnkamaLauncherServer
from ankama_launcher_emulator.utils.internet import get_available_network_interfaces


def run_gui() -> None:
    handler = AnkamaLauncherHandler()
    server = AnkamaLauncherServer(handler)
    server.start()

    accounts = CryptoHelper.getStoredApiKeys()
    interfaces = get_available_network_interfaces()

    app = QApplication(sys.argv)
    setTheme(Theme.DARK)

    window = MainWindow(server, accounts, interfaces)
    window.show()
    sys.exit(app.exec())
