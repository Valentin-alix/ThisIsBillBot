from PyQt6.QtWidgets import QStackedWidget, QVBoxLayout, QWidget
from qfluentwidgets import PivotItem, SegmentedWidget

from src.controller.player_info_storage import PlayerInfoSnapshot
from src.core import config
from src.core.bot.bot import Bot
from src.core.signals.log_signals import LogSignals
from src.gui.fragments.account_quick_info import AccountQuickInfoWidget
from src.gui.pages.craft.craft_page import CraftPage
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
        snapshot: PlayerInfoSnapshot | None,
        quarantine_reason: str | None,
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
        if config.DEBUG:
            self.quick_info_widget = AccountQuickInfoWidget(
                self.bot,
                snapshot,
                quarantine_reason,
                parent=self,
            )
            layout.addWidget(self.quick_info_widget)

        self.stacked_widget = QStackedWidget(self)
        layout.addWidget(self.stacked_widget)

        self.debug_pivot_item: PivotItem | None = None

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

        if config.DEBUG:
            self._init_debug_interface()

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

    def _select_initial_page(self) -> None:
        self.farmer_pivot_item.click()

    def set_snapshot_sub_area_name(self, sub_area_name: str | None) -> None:
        if self.quick_info_widget is not None:
            self.quick_info_widget.set_snapshot_sub_area_name(sub_area_name)
