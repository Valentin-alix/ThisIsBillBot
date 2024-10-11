from PyQt5.QtWidgets import QVBoxLayout
from qfluentwidgets import PivotItem

from src.gui.pages.logs.logs_table import LogsTable
from src.interfaces.enums.log_level import LogLevel
from src.signals.log_signals import LogSignals


class LogsWidget(PivotItem):
    def __init__(self, log_signals: LogSignals, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.v_layout = QVBoxLayout()
        self.v_layout.setContentsMargins(4, 4, 4, 4)
        self.v_layout.setSpacing(0)
        self.setLayout(self.v_layout)
        self.logs_table = LogsTable()
        self.layout().addWidget(self.logs_table)

        log_signals.log_emitted.connect(self.on_log_emitted)

    def on_log_emitted(self, log_level: LogLevel, msg: str):
        self.logs_table.add_row(log_level, msg)
