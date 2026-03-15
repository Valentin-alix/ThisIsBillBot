from collections import deque
from dataclasses import dataclass
from datetime import datetime

from PyQt6.QtCore import QAbstractListModel, QModelIndex, QSize, QSortFilterProxyModel, Qt, QTimer
from PyQt6.QtGui import QColor, QPainter, QPalette
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QListView,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QVBoxLayout,
    QWidget,
)
from qfluentwidgets import LineEdit

from src.services.logging_utils.log_level import LogLevel

_MAX_LOG_ENTRIES = 5_000
_LOG_ENTRY_ROLE = int(Qt.ItemDataRole.UserRole)
_LEVEL_COLOR_BY_LEVEL: dict[LogLevel, QColor] = {
    LogLevel.DEBUG: QColor(133, 133, 133),
    LogLevel.INFO: QColor(82, 156, 255),
    LogLevel.WARNING: QColor(255, 185, 0),
    LogLevel.ERROR: QColor(255, 99, 71),
    LogLevel.CRITICAL: QColor(255, 69, 58),
}


@dataclass(frozen=True)
class LogEntry:
    level: LogLevel
    message: str
    logged_at: datetime

    @property
    def display_text(self) -> str:
        return f"{self.logged_at:%H:%M:%S} | {self.level.name} | {self.message}"


class LogListModel(QAbstractListModel):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._entries: list[LogEntry] = []

    def rowCount(self, parent: QModelIndex | None = None) -> int:
        return len(self._entries)

    def data(self, index: QModelIndex, role: int | None = None) -> str | LogEntry | None:
        if not index.isValid():
            return None
        entry = self._entries[index.row()]
        if role in (None, Qt.ItemDataRole.DisplayRole):
            return entry.display_text
        if role == _LOG_ENTRY_ROLE:
            return entry
        return None

    def append_entries(self, entries: list[LogEntry]) -> None:
        if not entries:
            return
        overflow = len(self._entries) + len(entries) - _MAX_LOG_ENTRIES
        if overflow > 0:
            self.beginRemoveRows(QModelIndex(), 0, overflow - 1)
            del self._entries[:overflow]
            self.endRemoveRows()
        start = len(self._entries)
        self.beginInsertRows(QModelIndex(), start, start + len(entries) - 1)
        self._entries.extend(entries)
        self.endInsertRows()

    def clear(self) -> None:
        if not self._entries:
            return
        self.beginRemoveRows(QModelIndex(), 0, len(self._entries) - 1)
        self._entries.clear()
        self.endRemoveRows()


class LogFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._query = ""

    def set_query(self, query: str) -> None:
        normalized_query = query.casefold()
        if normalized_query == self._query:
            return
        self._query = normalized_query
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        if not self._query:
            return True
        source_model = self.sourceModel()
        assert source_model is not None
        entry = source_model.index(source_row, 0, source_parent).data(_LOG_ENTRY_ROLE)
        if not isinstance(entry, LogEntry):
            raise TypeError("Expected a LogEntry payload in the log model")
        return self._query in entry.display_text.casefold()


class LogEntryDelegate(QStyledItemDelegate):
    def sizeHint(
        self,
        option: QStyleOptionViewItem,
        index: QModelIndex,
    ) -> QSize:
        del option, index
        return QSize(0, 32)

    def paint(self, painter: QPainter | None, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        if painter is None:
            return
        entry = index.data(_LOG_ENTRY_ROLE)
        if not isinstance(entry, LogEntry):
            return super().paint(painter, option, index)

        painter.save()
        rect = option.rect.adjusted(12, 4, -12, -4)
        text_color = option.palette.color(QPalette.ColorRole.Text)
        muted_color = option.palette.color(QPalette.ColorRole.PlaceholderText)
        metrics = option.fontMetrics

        timestamp_width = metrics.horizontalAdvance("00:00:00") + 12
        timestamp_rect = rect.adjusted(0, 0, -(rect.width() - timestamp_width), 0)
        painter.setPen(muted_color)
        painter.drawText(timestamp_rect, Qt.AlignmentFlag.AlignVCenter, entry.logged_at.strftime("%H:%M:%S"))

        badge_text = entry.level.name
        badge_width = max(68, metrics.horizontalAdvance(badge_text) + 16)
        badge_rect = rect.adjusted(timestamp_width, 2, -(rect.width() - timestamp_width - badge_width), -2)
        badge_color = _LEVEL_COLOR_BY_LEVEL[entry.level]
        badge_background = QColor(badge_color)
        badge_background.setAlpha(55)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(badge_background)
        painter.drawRoundedRect(badge_rect, 6, 6)
        painter.setPen(badge_color)
        painter.drawText(badge_rect, Qt.AlignmentFlag.AlignCenter, badge_text)

        message_rect = rect.adjusted(timestamp_width + badge_width + 12, 0, 0, 0)
        painter.setPen(text_color)
        painter.drawText(
            message_rect,
            Qt.AlignmentFlag.AlignVCenter,
            metrics.elidedText(entry.message, Qt.TextElideMode.ElideRight, message_rect.width()),
        )
        painter.restore()


class LogsTable(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self.search_edit = LineEdit(self)
        self.search_edit.setPlaceholderText("Search logs")
        self.search_edit.setClearButtonEnabled(True)
        layout.addWidget(self.search_edit)

        self.log_model = LogListModel(self)
        self.proxy_model = LogFilterProxyModel(self)
        self.proxy_model.setSourceModel(self.log_model)
        self.list_view = QListView(self)
        self.list_view.setModel(self.proxy_model)
        self.list_view.setItemDelegate(LogEntryDelegate(self.list_view))
        self.list_view.setUniformItemSizes(True)
        self.list_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.list_view.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.list_view.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        layout.addWidget(self.list_view)

        self._pending_entries: deque[LogEntry] = deque(maxlen=_MAX_LOG_ENTRIES)
        self._updates_active = False
        self._batch_timer = QTimer(self)
        self._batch_timer.setInterval(100)
        self._batch_timer.setSingleShot(True)
        self._batch_timer.timeout.connect(self._flush_pending_entries)

        self.search_edit.textChanged.connect(self._apply_filter)

    def add_row(self, level: LogLevel, msg: str, logged_at: datetime | None = None) -> None:
        self._pending_entries.append(LogEntry(level, msg, logged_at or datetime.now()))
        if self._updates_active and not self._batch_timer.isActive():
            self._batch_timer.start()

    def set_updates_active(self, active: bool) -> None:
        self._updates_active = active
        if active and self._pending_entries and not self._batch_timer.isActive():
            self._batch_timer.start()
        elif not active:
            self._batch_timer.stop()

    def clear(self) -> None:
        self._batch_timer.stop()
        self._pending_entries.clear()
        self.log_model.clear()

    def _apply_filter(self, query: str) -> None:
        self._flush_pending_entries()
        scroll_bar = self.list_view.verticalScrollBar()
        assert scroll_bar is not None
        was_at_bottom = scroll_bar.value() == scroll_bar.maximum()
        self.proxy_model.set_query(query)
        if was_at_bottom:
            self.list_view.scrollToBottom()

    def _flush_pending_entries(self) -> None:
        if not self._pending_entries:
            return
        scroll_bar = self.list_view.verticalScrollBar()
        assert scroll_bar is not None
        was_at_bottom = scroll_bar.value() == scroll_bar.maximum()
        self.log_model.append_entries(list(self._pending_entries))
        self._pending_entries.clear()
        if was_at_bottom:
            self.list_view.scrollToBottom()
