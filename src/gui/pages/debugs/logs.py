from datetime import datetime

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFileDialog, QHBoxLayout, QVBoxLayout, QWidget
from qfluentwidgets import FluentIcon, PrimaryPushButton

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

        top_bar = QWidget(self)
        hbox_layout = QHBoxLayout()
        top_bar.setLayout(hbox_layout)
        hbox_layout.setContentsMargins(0, 0, 0, 0)
        hbox_layout.addStretch()

        export_btn = PrimaryPushButton(FluentIcon.SAVE, "Exporter les logs", top_bar)
        export_btn.clicked.connect(self.on_export_logs)
        hbox_layout.addWidget(export_btn)

        self.v_layout.addWidget(top_bar)

        self.logs_table = LogsTable(parent=self)
        self.v_layout.addWidget(self.logs_table)

        log_signals.log_emitted.connect(profiled_slot(self.on_log_emitted))
        self.global_signals.log_emitted.connect(profiled_slot(self.on_log_emitted))

    def on_log_emitted(self, log_level: LogLevel, msg: str) -> None:
        self.logs_table.add_row(log_level, msg)

    def on_export_logs(self) -> None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"logs_{timestamp}.txt"

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Exporter les logs", default_filename, "Fichiers texte (*.txt)"
        )

        if not file_path:
            return

        model = self.logs_table.table.item_model
        row_count = model.rowCount()

        with open(file_path, "w", encoding="utf-8") as file:
            for row in range(row_count):
                time_text = model.data(model.index(row, 0), Qt.ItemDataRole.DisplayRole)
                type_text = model.data(model.index(row, 1), Qt.ItemDataRole.DisplayRole)
                msg_text = model.data(model.index(row, 2), Qt.ItemDataRole.DisplayRole)
                file.write(f"[{time_text}] [{type_text}] {msg_text}\n")
