from PyQt6.QtWidgets import QVBoxLayout, QWidget

from src.core.signals.global_log_signals import GlobalLogSignals
from src.core.signals.log_signals import LogSignals
from src.gui.pages.debugs.logs_table import LogsTable
from src.gui.utils.profiling import profiled_slot
from src.services.logging.log_level import LogLevel


class LogsWidget(QWidget):
    def __init__(
        self,
        global_signals: GlobalLogSignals,
        log_signals: LogSignals,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent=parent)
        self.v_layout = QVBoxLayout()
        self.v_layout.setContentsMargins(4, 4, 4, 4)
        self.v_layout.setSpacing(4)
        self.global_signals = global_signals
        self.setLayout(self.v_layout)

        self.logs_table = LogsTable(parent=self)
        self.v_layout.addWidget(self.logs_table)

        log_signals.log_emitted.connect(profiled_slot(self.on_log_emitted))
        self.global_signals.log_emitted.connect(profiled_slot(self.on_log_emitted))

    def on_log_emitted(self, log_level: LogLevel, msg: str) -> None:
        self.logs_table.add_row(log_level, msg)
