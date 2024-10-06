from PyQt5.QtWidgets import QStackedWidget, QVBoxLayout, QWidget
from qfluentwidgets import SegmentedWidget

from src.gui.pages.farmer.farmer import FarmerWidget
from src.gui.pages.sniffer.sniffer import SnifferWidget
from src.signals.grid_signals import GridSignals
from src.signals.harvester_signals import HarvesterSignals
from src.signals.message_signals import MessageInfoSignals
from src.signals.player_signals import GameInfoSignals


class AccountWidget(QWidget):
    def __init__(
        self,
        login: str,
        msg_info_signals: MessageInfoSignals,
        game_infos_signals: GameInfoSignals,
        harvester_signals: HarvesterSignals,
        grid_signals: GridSignals,
    ):
        super().__init__()
        self.login = login
        self.setObjectName(f"{login}_bot")
        self.setLayout(QVBoxLayout())

        pivot = SegmentedWidget()
        self.layout().addWidget(pivot)

        stacked_widget = QStackedWidget(self)
        self.layout().addWidget(stacked_widget)

        # sniffer
        sniffer_interface = SnifferWidget(msg_info_signals)
        stacked_widget.addWidget(sniffer_interface)
        sniffer_route = f"{login}_sniffer"
        pivot.addItem(
            routeKey=sniffer_route,
            text="Sniffer",
            onClick=lambda: stacked_widget.setCurrentWidget(sniffer_interface),
        )
        pivot.setCurrentItem(sniffer_route)

        # farmer
        harvester_interface = FarmerWidget(
            grid_signals, game_infos_signals, harvester_signals
        )
        stacked_widget.addWidget(harvester_interface)
        sniffer_route = f"{login}_harvester"
        pivot.addItem(
            routeKey=sniffer_route,
            text="Farmer",
            onClick=lambda: stacked_widget.setCurrentWidget(harvester_interface),
        )
