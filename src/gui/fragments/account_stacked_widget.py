from typing import cast

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QStackedWidget, QVBoxLayout, QWidget
from qfluentwidgets import PivotItem, SegmentedWidget

from src import const
from src.core.bot.bot import Bot
from src.core.signals.global_log_signals import GlobalLogSignals
from src.gui.pages.craft.craft_page import CraftPage
from src.gui.pages.debugs.sniffer import SnifferWidget
from src.gui.pages.farmer.farmer import FarmerWidget


class AccountStackedWidget(QWidget):
    def __init__(self, global_log_signals: GlobalLogSignals, login: str, bot: Bot):
        super().__init__()
        self.login = login
        self.bot = bot
        self.global_log_signals = global_log_signals
        self.setObjectName(f"{login}_bot")
        self.setLayout(QVBoxLayout())

        self.pivot = SegmentedWidget()
        self.layout().addWidget(self.pivot)

        self.stacked_widget = QStackedWidget(self)
        self.layout().addWidget(self.stacked_widget)

        self.sniffer_interface = SnifferWidget(bot, self.global_log_signals)
        self.stacked_widget.addWidget(self.sniffer_interface)
        self.sniffer_route = f"{login}_sniffer"
        self.debug_pivot_item = cast(
            PivotItem,
            self.pivot.addItem(
                routeKey=self.sniffer_route,
                text="Debug",
                onClick=lambda: self.stacked_widget.setCurrentWidget(
                    self.sniffer_interface
                ),
            ),
        )

        self.harvester_interface = FarmerWidget(login, self.bot)
        self.stacked_widget.addWidget(self.harvester_interface)
        self.harvester_route = f"{login}_harvester"
        self.farmer_pivot_item = cast(
            PivotItem,
            self.pivot.addItem(
                routeKey=self.harvester_route,
                text="Farmer",
                onClick=lambda: self.stacked_widget.setCurrentWidget(
                    self.harvester_interface
                ),
            ),
        )

        self.craft_interface = CraftPage(self.bot)
        self.stacked_widget.addWidget(self.craft_interface)
        self.craft_route = f"{login}_craft"
        self.craft_pivot_item = cast(
            PivotItem,
            self.pivot.addItem(
                routeKey=self.craft_route,
                text="Craft",
                onClick=lambda: self.stacked_widget.setCurrentWidget(
                    self.craft_interface
                ),
            ),
        )

        self.is_debug_visible = None
        self.set_debug_visibility(const.DEBUG)

    def set_debug_visibility(self, is_visible: bool) -> None:
        if self.is_debug_visible == is_visible:
            return

        self.is_debug_visible = is_visible

        if self.debug_pivot_item is not None:
            self.debug_pivot_item.setVisible(is_visible)

        self.harvester_interface.set_debug_tabs_visibility(is_visible)

        QTimer.singleShot(0, lambda: self.set_page_after_debug(is_visible))

    def set_page_after_debug(self, is_visible: bool):
        if is_visible:
            if self.pivot.currentRouteKey() == self.sniffer_route:
                self.farmer_pivot_item.click()
            self.debug_pivot_item.click()
        else:
            if self.pivot.currentRouteKey() == self.harvester_route:
                self.craft_pivot_item.click()
            self.farmer_pivot_item.click()
