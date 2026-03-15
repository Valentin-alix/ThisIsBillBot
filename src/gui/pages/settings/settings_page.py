from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QScrollArea, QStackedWidget, QVBoxLayout, QWidget
from qfluentwidgets import SegmentedWidget, SubtitleLabel

from src.gui.pages.settings.assignment_panel import AssignmentSettingsPanel
from src.gui.pages.settings.behavior_panel import BehaviorSettingsPanel
from src.gui.pages.settings.mail_panel import MailSettingsPanel
from src.gui.pages.settings.payment_panel import PaymentSettingsPanel
from src.gui.pages.settings.proxy_panel import ProxySettingsPanel
from src.gui.pages.settings.schedule_panel import ScheduleSettingsPanel
from src.gui.pages.settings.services_panel import ServicesSettingsPanel


class SettingsPage(QWidget):
    schedules_changed = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("settings")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.addWidget(SubtitleLabel("Settings", self))
        self.navigation = SegmentedWidget(self)
        layout.addWidget(self.navigation)
        self.stack = QStackedWidget(self)
        layout.addWidget(self.stack)
        self.behaviors = BehaviorSettingsPanel()
        self.mail = MailSettingsPanel()
        self.proxies = ProxySettingsPanel()
        self.schedules = ScheduleSettingsPanel()
        self.assignments = AssignmentSettingsPanel()
        self.services = ServicesSettingsPanel()
        self.payments = PaymentSettingsPanel()
        self.schedules.changed.connect(self.schedules_changed.emit)
        self.assignments.changed.connect(self.schedules_changed.emit)
        for index, (label, panel) in enumerate(
            [
                ("Behaviors", self.behaviors),
                ("Email", self.mail),
                ("Proxies", self.proxies),
                ("Schedules", self.schedules),
                ("Accounts", self.assignments),
                ("Services", self.services),
                ("Payments", self.payments),
            ]
        ):
            scroll = QScrollArea(self)
            scroll.setWidgetResizable(True)
            scroll.setWidget(panel)
            scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
            panel.setAutoFillBackground(False)
            self.stack.addWidget(scroll)
            self.navigation.addItem(
                str(index),
                label,
                onClick=lambda _checked=False, index=index: self.stack.setCurrentIndex(index),
            )
            self.navigation.widget(str(index)).setFixedHeight(44)
        self.navigation.setCurrentItem("0")
