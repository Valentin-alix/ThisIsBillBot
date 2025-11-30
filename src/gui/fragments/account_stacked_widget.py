from PyQt6.QtWidgets import QStackedWidget, QVBoxLayout, QWidget
from qfluentwidgets import PivotItem, SegmentedWidget

from src import consts
from src.core.bot.bot import Bot
from src.core.signals.log_signals import LogSignals
from src.gui.fragments.account_quick_info import AccountQuickInfoWidget
from src.gui.pages.craft.craft_page import CraftPage
from src.gui.pages.debugs.sandbox import SandboxWidget
from src.gui.pages.debugs.sniffer import SnifferWidget
from src.gui.pages.farmer.farmer import FarmerWidget


class AccountStackedWidget(QWidget):
    @staticmethod
    def _require_pivot_item(item: PivotItem | None, route_key: str) -> PivotItem:
        if item is None:
            raise ValueError(f"Segmented route `{route_key}` is already registered")
        return item

    def __init__(
        self,
        global_log_signals: LogSignals,
        login: str,
        bot: Bot,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent=parent)
        self.login = login
        self.bot = bot
        self.global_log_signals = global_log_signals
        self.setObjectName(f"{login}_bot")
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.pivot = SegmentedWidget(self)
        layout.addWidget(self.pivot)

        self.quick_info_widget: AccountQuickInfoWidget | None = None
        if consts.DEBUG:
            self.quick_info_widget = AccountQuickInfoWidget(self.bot, parent=self)
            layout.addWidget(self.quick_info_widget)

        self.stacked_widget = QStackedWidget(self)
        layout.addWidget(self.stacked_widget)

        self.debug_pivot_item: PivotItem | None = None
        if consts.DEBUG:
            self._init_debug_interface()

        self.harvester_interface = FarmerWidget(login, self.bot, parent=self.stacked_widget)
        self.stacked_widget.addWidget(self.harvester_interface)
        self.harvester_route = f"{login}_harvester"
        self.farmer_pivot_item = self._require_pivot_item(
            self.pivot.addItem(
                routeKey=self.harvester_route,
                text="Farmer",
                onClick=lambda: self.stacked_widget.setCurrentWidget(self.harvester_interface),
            ),
            self.harvester_route,
        )

        self.craft_interface = CraftPage(self.bot, parent=self.stacked_widget)
        self.stacked_widget.addWidget(self.craft_interface)
        self.craft_route = f"{login}_craft"
        self.craft_pivot_item = self._require_pivot_item(
            self.pivot.addItem(
                routeKey=self.craft_route,
                text="Craft",
                onClick=lambda: self.stacked_widget.setCurrentWidget(self.craft_interface),
            ),
            self.craft_route,
        )

        if consts.DEBUG:
            self._init_sandbox_interface()

        for pivot_item in self.pivot.items.values():
            pivot_item.setFixedHeight(40)

        self._select_initial_page()

    def _init_debug_interface(self) -> None:
        sniffer_interface = SnifferWidget(self.bot, self.global_log_signals, parent=self.stacked_widget)
        self.stacked_widget.addWidget(sniffer_interface)
        self.sniffer_route = f"{self.login}_sniffer"
        self.debug_pivot_item = self._require_pivot_item(
            self.pivot.addItem(
                routeKey=self.sniffer_route,
                text="Debug",
                onClick=lambda: self.stacked_widget.setCurrentWidget(sniffer_interface),
            ),
            self.sniffer_route,
        )

    def _init_sandbox_interface(self) -> None:
        sandbox_interface = SandboxWidget(self.bot, parent=self.stacked_widget)
        self.stacked_widget.addWidget(sandbox_interface)
        self.sandbox_route = f"{self.login}_sandbox"
        self._require_pivot_item(
            self.pivot.addItem(
                routeKey=self.sandbox_route,
                text="Sandbox",
                onClick=lambda: self.stacked_widget.setCurrentWidget(sandbox_interface),
            ),
            self.sandbox_route,
        )

    def _select_initial_page(self) -> None:
        if consts.DEBUG:
            assert self.debug_pivot_item
            self.debug_pivot_item.click()
        else:
            self.farmer_pivot_item.click()
