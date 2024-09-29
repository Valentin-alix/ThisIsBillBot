from PyQt5.QtWidgets import QStackedWidget, QVBoxLayout, QWidget
from qfluentwidgets import SegmentedWidget

from src.gui.pages.sniffer.sniffer import SnifferWidget
from src.interfaces.models.bot import Bot


class AccountWidget(QWidget):
    def __init__(self, account: Bot):
        super().__init__()
        self.setObjectName(f"{account.account_nickname}_bot")
        self.setLayout(QVBoxLayout())

        pivot = SegmentedWidget()
        self.layout().addWidget(pivot)

        stacked_widget = QStackedWidget(self)
        self.layout().addWidget(stacked_widget)

        sniffer_interface = SnifferWidget(account.msg_info_signals)
        stacked_widget.addWidget(sniffer_interface)
        sniffer_route = f"{account.account_nickname}_sniffer"
        pivot.addItem(
            routeKey=sniffer_route,
            text="Sniffer",
            onClick=lambda: stacked_widget.setCurrentWidget(sniffer_interface),
        )
        pivot.setCurrentItem(sniffer_route)
