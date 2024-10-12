from PyQt5.QtWidgets import QStackedWidget, QVBoxLayout, QWidget
from qfluentwidgets import SegmentedWidget

from src.common.logger import Logger
from src.gui.pages.craft.craft_page import CraftPage
from src.gui.pages.farmer.farmer import FarmerWidget
from src.gui.pages.logs.logs import LogsWidget
from src.gui.pages.sniffer.sniffer import SnifferWidget
from src.signals.bot_signals import BotSignals
from src.signals.grid_signals import GridSignals
from src.signals.log_signals import LogSignals
from src.signals.message_signals import MessageInfoSignals
from src.signals.player_signals import GameInfoSignals
from src.signals.shared_farm_signals import SharedFarmSignals
from src.signals.world_signals import WorldSignals


class AccountFrame(QWidget):
    def __init__(
        self,
        login: str,
        account_id: int,
        logger: Logger,
        msg_info_signals: MessageInfoSignals,
        game_infos_signals: GameInfoSignals,
        farm_signals: BotSignals,
        grid_signals: GridSignals,
        world_signals: WorldSignals,
        log_signals: LogSignals,
        shared_farm_signals: SharedFarmSignals,
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
            account_id,
            grid_signals,
            game_infos_signals,
            world_signals,
            farm_signals,
            shared_farm_signals=shared_farm_signals,
        )
        stacked_widget.addWidget(harvester_interface)
        sniffer_route = f"{login}_harvester"
        pivot.addItem(
            routeKey=sniffer_route,
            text="Farmer",
            onClick=lambda: stacked_widget.setCurrentWidget(harvester_interface),
        )

        # craft
        craft_interface = CraftPage(farm_signals=farm_signals, logger=logger)
        stacked_widget.addWidget(craft_interface)
        sniffer_route = f"{login}_craft"
        pivot.addItem(
            routeKey=sniffer_route,
            text="Craft",
            onClick=lambda: stacked_widget.setCurrentWidget(craft_interface),
        )

        # logs
        logs_interface = LogsWidget(log_signals=log_signals)
        stacked_widget.addWidget(logs_interface)
        logs_route = f"{login}_logs"
        pivot.addItem(
            routeKey=logs_route,
            text="Logs",
            onClick=lambda: stacked_widget.setCurrentWidget(logs_interface),
        )
