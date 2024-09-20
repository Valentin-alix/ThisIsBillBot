from qfluentwidgets import FluentIcon, FluentWindow

from src.gui.pages.sniffer.sniffer_widget import SnifferWidget
from src.gui.signals.msg_signals import MessageSignals


class MainWindow(FluentWindow):
    BASE_WIDTH: int = 1280
    BASE_HEIGHT: int = 720

    def __init__(
        self, msg_signals: MessageSignals, title: str, *args, **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self.title = title

        self.init_window()
        self.init_nagivation(msg_signals)

    def init_window(self):
        self.setWindowTitle(self.title)
        self.resize(self.BASE_WIDTH, self.BASE_HEIGHT)

    def init_nagivation(self, msg_signals: MessageSignals):
        self.sniffer_interface = SnifferWidget(msg_signals)
        self.sniffer_interface.setObjectName("sniffer")
        self.addSubInterface(self.sniffer_interface, FluentIcon.SEARCH, "Sniffer")
