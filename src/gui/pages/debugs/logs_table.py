from collections import deque
from datetime import datetime

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QPlainTextEdit, QVBoxLayout, QWidget
from qfluentwidgets import LineEdit

from src.services.logging_utils.log_level import LogLevel


class LogsTable(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self.search_edit = LineEdit(self)
        self.search_edit.setPlaceholderText("Rechercher dans les logs")
        layout.addWidget(self.search_edit)

        self.text_view = QPlainTextEdit(self)
        self.text_view.setReadOnly(True)
        self.text_view.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        font = self.text_view.font()
        font.setPointSizeF(font.pointSizeF() + 1.5)
        self.text_view.setFont(font)
        document = self.text_view.document()
        assert document is not None
        document.setMaximumBlockCount(5000)
        layout.addWidget(self.text_view)

        self._all_lines: deque[str] = deque(maxlen=5000)
        self._pending_lines: deque[str] = deque(maxlen=5000)
        self._updates_active = False
        self._batch_timer = QTimer(self)
        self._batch_timer.setInterval(100)
        self._batch_timer.setSingleShot(True)
        self._batch_timer.timeout.connect(self._flush_pending_lines)

        self.search_edit.textChanged.connect(self._apply_filter)

    def add_row(self, level: LogLevel, msg: str, logged_at: datetime | None = None) -> None:
        timestamp = logged_at or datetime.now()
        line = f"{timestamp:%H:%M:%S} | {level.name} | {msg}"
        self._all_lines.append(line)
        query = self.search_edit.text()
        if query and query.lower() not in line.lower():
            return
        if self._updates_active and not self._batch_timer.isActive():
            self._batch_timer.start()
        self._pending_lines.append(line)

    def set_updates_active(self, active: bool) -> None:
        self._updates_active = active
        if active and self._pending_lines and not self._batch_timer.isActive():
            self._batch_timer.start()
        elif not active:
            self._batch_timer.stop()

    def clear(self) -> None:
        self._batch_timer.stop()
        self._all_lines.clear()
        self._pending_lines.clear()
        self.text_view.clear()

    def _apply_filter(self) -> None:
        query = self.search_edit.text()
        scroll_bar = self.text_view.verticalScrollBar()
        assert scroll_bar is not None
        was_at_bottom = scroll_bar.value() == scroll_bar.maximum()
        if query:
            query_lower = query.lower()
            lines = [line for line in self._all_lines if query_lower in line.lower()]
        else:
            lines = list(self._all_lines)
        self._pending_lines.clear()
        self.text_view.setPlainText("\n".join(lines))
        if was_at_bottom:
            scroll_bar.setValue(scroll_bar.maximum())

    def _flush_pending_lines(self) -> None:
        if not self._pending_lines:
            return
        scroll_bar = self.text_view.verticalScrollBar()
        assert scroll_bar is not None
        was_at_bottom = scroll_bar.value() == scroll_bar.maximum()
        self.text_view.appendPlainText("\n".join(self._pending_lines))
        self._pending_lines.clear()
        if was_at_bottom:
            scroll_bar.setValue(scroll_bar.maximum())
