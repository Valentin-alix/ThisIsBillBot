from PyQt5.QtWidgets import QStackedWidget, QVBoxLayout, QWidget
from qfluentwidgets import SegmentedWidget

from src.bot import Bot
from src.const import DEBUG
from src.gui.pages.craft.craft_page import CraftPage
from src.gui.pages.debugs.sniffer import SnifferWidget
from src.gui.pages.farmer.farmer import FarmerWidget


class AccountStackedWidget(QWidget):
    def __init__(self, login: str, bot: Bot):
        super().__init__()
        self.login = login
        self.bot = bot
        self.setObjectName(f"{login}_bot")
        self.setLayout(QVBoxLayout())

        pivot = SegmentedWidget()
        self.layout().addWidget(pivot)

        stacked_widget = QStackedWidget(self)
        self.layout().addWidget(stacked_widget)

        if DEBUG:
            # sniffer (merged with logs on the right)
            sniffer_interface = SnifferWidget(bot)
            stacked_widget.addWidget(sniffer_interface)
            sniffer_route = f"{login}_sniffer"
            pivot.addItem(
                routeKey=sniffer_route,
                text="Debug",
                onClick=lambda: stacked_widget.setCurrentWidget(sniffer_interface),
            )
        else:
            sniffer_route = None

        # farmer
        harvester_interface = FarmerWidget(login, self.bot)
        stacked_widget.addWidget(harvester_interface)
        harvester_route = f"{login}_harvester"
        pivot.addItem(
            routeKey=harvester_route,
            text="Farmer",
            onClick=lambda: stacked_widget.setCurrentWidget(harvester_interface),
        )

        if sniffer_route:
            pivot.setCurrentItem(sniffer_route)
        else:
            pivot.setCurrentItem(harvester_route)

        # craft
        craft_interface = CraftPage(self.bot)
        stacked_widget.addWidget(craft_interface)
        craft_route = f"{login}_craft"
        pivot.addItem(
            routeKey=craft_route,
            text="Craft",
            onClick=lambda: stacked_widget.setCurrentWidget(craft_interface),
        )
