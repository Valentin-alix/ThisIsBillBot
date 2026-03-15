import json
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from functools import cached_property

from PyQt6.QtCore import QModelIndex, QObject, Qt, QTimer
from PyQt6.QtGui import QBrush
from PyQt6.QtWidgets import QHeaderView, QWidget
from qfluentwidgets import TableWidget

from src.gui.components.table.column_info import ColumnInfo
from src.gui.components.table.table import BaseTableWidget
from src.gui.components.table.table_view import CustomTableModel
from src.gui.consts import GREEN_COLOR
from src.gui.pages.debugs.message_filter_proxy import MESSAGE_SEARCH_ROLE, MessageFilterProxyModel
from src.protocol.message import MessageInfo
from src.services.debug_recorder.recorder import RecentMessageEntry


@dataclass
class MessageRow:
    received_time: datetime
    from_server: bool
    was_send_from_proxy: bool
    display_name: str
    _msg_info: MessageInfo | None = None
    _recent_entry: RecentMessageEntry | None = None
    time_text: str = field(init=False)
    origin_text: str = field(init=False)

    def __post_init__(self) -> None:
        self.time_text = self.received_time.strftime("%H:%M:%S.%f")[:-3]
        self.origin_text = "Server" if self.from_server else "Client"

    def message_info(self) -> MessageInfo:
        if self._msg_info is None:
            assert self._recent_entry is not None
            self._msg_info = self._recent_entry.to_message_info()
        return self._msg_info

    @cached_property
    def search_text(self) -> str:
        if self._recent_entry is not None:
            return self._recent_entry.serialized
        msg_info = self.message_info()
        return json.dumps(msg_info.msg_json, ensure_ascii=False) + json.dumps(
            msg_info.obf_msg_json, ensure_ascii=False
        )


class MessageTableModel(CustomTableModel):
    def __init__(self, parent: QObject | None = None, max_row_count: int = 5000) -> None:
        super().__init__(column_count=4, parent=parent, max_row_count=max_row_count)
        self._rows: list[MessageRow] = []

    def rowCount(self, parent: QModelIndex | None = None) -> int:
        return len(self._rows)

    def columnCount(self, parent: QModelIndex | None = None) -> int:
        return self._column_count

    def data(self, index: QModelIndex, role: int | None = None) -> object | None:
        if not index.isValid():
            return None
        role = role if role is not None else int(Qt.ItemDataRole.DisplayRole)
        row = self._rows[index.row()]
        if role == Qt.ItemDataRole.DisplayRole:
            return (row.time_text, row.origin_text, row.display_name, "")[index.column()]
        if role == Qt.ItemDataRole.UserRole and index.column() == 3:
            return row.message_info()
        if role == MESSAGE_SEARCH_ROLE and index.column() == 3:
            return row.search_text
        if role == Qt.ItemDataRole.BackgroundRole and row.was_send_from_proxy and index.column() < 3:
            return QBrush(GREEN_COLOR)
        return None

    def append_messages(self, rows: list[MessageRow]) -> None:
        if not rows:
            return
        start = len(self._rows)
        self.beginInsertRows(QModelIndex(), start, start + len(rows) - 1)
        self._rows.extend(rows)
        self.endInsertRows()
        self.signals.batched_rows.emit()
        if len(self._rows) > self._max_row_count:
            self.signals.max_row_reached.emit()

    def remove_rows(self, row: int, count: int) -> None:
        self.beginRemoveRows(QModelIndex(), row, row + count - 1)
        del self._rows[row : row + count]
        self.endRemoveRows()

    def clear_all(self) -> None:
        if self._rows:
            self.remove_rows(0, len(self._rows))


class MessageTable(BaseTableWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        self.message_model = MessageTableModel()
        super().__init__(
            proxy_model=MessageFilterProxyModel(),
            item_model=self.message_model,
            parent=parent,
        )
        self._pending_messages: deque[MessageRow] = deque(maxlen=5000)
        self._updates_active = False
        self._batch_timer = QTimer(self)
        self._batch_timer.setInterval(100)
        self._batch_timer.setSingleShot(True)
        self._batch_timer.timeout.connect(self._flush_pending_messages)
        self._unmapped_candidates_by_obf: dict[str, list[tuple[str, float]]] = {}
        columns: list[ColumnInfo] = [
            ColumnInfo(name="Heure"),
            ColumnInfo(name="Origine"),
            ColumnInfo(name="Type"),
            ColumnInfo(name="Contenu", is_hidden=True),
        ]
        self.table.set_columns(columns)

        header = self.table.horizontalHeader()
        assert header is not None
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)

        self.table.setColumnWidth(0, 110)
        self.table.setColumnWidth(1, 110)

        self.table.setEditTriggers(TableWidget.EditTrigger.NoEditTriggers)

    def add_row(self, msg_info: MessageInfo, was_send_from_proxy: bool) -> None:
        display_name = msg_info.sub_msg_name
        if msg_info.msg_json is None:
            candidates = self._unmapped_candidates_by_obf.get(msg_info.sub_msg_name)
            if candidates:
                candidates_str = ", ".join(f"{name} ({sim:.0%})" for name, sim in candidates)
                display_name = f"{msg_info.sub_msg_name} ? {candidates_str}"
        self._pending_messages.append(
            MessageRow(
                received_time=msg_info.received_time,
                from_server=msg_info.from_server,
                was_send_from_proxy=was_send_from_proxy,
                display_name=display_name,
                _msg_info=msg_info,
            )
        )
        self._start_batch_if_needed()

    def add_recent_entries(self, entries: list[RecentMessageEntry]) -> None:
        self._pending_messages.extend(
            MessageRow(
                received_time=entry.received_time,
                from_server=entry.from_server,
                was_send_from_proxy=entry.was_sent_from_proxy,
                display_name=entry.sub_msg_name,
                _recent_entry=entry,
            )
            for entry in entries
        )
        self._start_batch_if_needed()

    def _start_batch_if_needed(self) -> None:
        if self._updates_active and not self._batch_timer.isActive():
            self._batch_timer.start()

    def set_updates_active(self, active: bool) -> None:
        self._updates_active = active
        if active and self._pending_messages and not self._batch_timer.isActive():
            self._batch_timer.start()
        elif not active:
            self._batch_timer.stop()

    def clear(self) -> None:
        self._batch_timer.stop()
        self._pending_messages.clear()
        self.message_model.clear_all()

    def _flush_pending_messages(self) -> None:
        if not self._pending_messages:
            return

        self.message_model.append_messages(list(self._pending_messages))
        self._pending_messages.clear()
