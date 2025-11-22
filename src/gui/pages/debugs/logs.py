from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QHideEvent, QShowEvent
from PyQt6.QtWidgets import QVBoxLayout, QWidget

from src.core.signals.log_signals import LogSignals
from src.gui.pages.debugs.logs_table import LogsTable


class LogsWidget(QWidget):
    def __init__(
        self,
        global_signals: LogSignals,
        log_signals: LogSignals,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent=parent)
        self.v_layout = QVBoxLayout()
        self.v_layout.setContentsMargins(4, 4, 4, 4)
        self.v_layout.setSpacing(4)
        self._capture_enabled = True
        self._global_signals = global_signals
        self._log_signals = log_signals
        self._global_cursor = 0
        self._log_cursor = 0
        self.setLayout(self.v_layout)

        self.logs_table = LogsTable(parent=self)
        self.v_layout.addWidget(self.logs_table)

        self._poll_timer = QTimer(self)
        self._poll_timer.setInterval(100)
        self._poll_timer.timeout.connect(self._poll_logs)

    def set_capture_enabled(self, enabled: bool) -> None:
        self._capture_enabled = enabled
        if enabled:
            self._global_cursor = self._global_signals.latest_sequence
            self._log_cursor = self._log_signals.latest_sequence
            if self.isVisible():
                self._poll_timer.start()
        else:
            self._poll_timer.stop()
            self._global_cursor = self._global_signals.latest_sequence
            self._log_cursor = self._log_signals.latest_sequence

    def _poll_logs(self) -> None:
        self._global_cursor, global_entries = self._global_signals.recent_after(self._global_cursor)
        self._log_cursor, bot_entries = self._log_signals.recent_after(self._log_cursor)
        for entry in sorted((*global_entries, *bot_entries), key=lambda entry: entry.logged_at):
            self.logs_table.add_row(entry.level, entry.message, entry.logged_at)

    def showEvent(self, a0: QShowEvent | None) -> None:
        self.logs_table.set_updates_active(True)
        if self._capture_enabled:
            self._poll_logs()
            self._poll_timer.start()
        super().showEvent(a0)

    def hideEvent(self, a0: QHideEvent | None) -> None:
        self._poll_timer.stop()
        self.logs_table.set_updates_active(False)
        super().hideEvent(a0)
