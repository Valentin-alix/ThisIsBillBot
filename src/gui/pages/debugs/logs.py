from PyQt5.QtWidgets import QVBoxLayout
from qfluentwidgets import PivotItem

from src.core.signals.log_signals import LogSignals
from src.gui.pages.debugs.logs_table import LogsTable
from src.gui.utils.profiling import profiled_slot
from src.services.logging.log_level import LogLevel


class LogsWidget(PivotItem):
    def __init__(self, log_signals: LogSignals, *args, **kwargs):  # type: ignore
        super().__init__(*args, **kwargs)
        self.v_layout = QVBoxLayout()
        self.v_layout.setContentsMargins(4, 4, 4, 4)
        self.v_layout.setSpacing(0)
        self.setLayout(self.v_layout)
        self.logs_table = LogsTable()
        self.layout().addWidget(self.logs_table)

        log_signals.log_emitted.connect(profiled_slot(self.on_log_emitted))
        log_signals.clear_logs.connect(self.logs_table.table.item_model.clear_all)

    def on_log_emitted(self, log_level: LogLevel, msg: str):
        self.logs_table.add_row(log_level, msg)
