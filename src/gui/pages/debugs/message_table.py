from typing import TypeAlias

from cachetools import LRUCache, cached
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QStandardItem
from PyQt6.QtWidgets import QHeaderView, QWidget
from qfluentwidgets import TableWidget

from src.protocol.message import MessageInfo
from src.gui.components.table.column_info import ColumnInfo
from src.gui.components.table.table import BaseTableWidget
from src.gui.consts import GREEN_COLOR
from src.gui.pages.debugs.message_filter_proxy import MessageFilterProxyModel

MessageTreeValue: TypeAlias = (
    str | int | float | bool | None | dict[str, "MessageTreeValue"] | list["MessageTreeValue"]
)


def _deep_count_fields_cache_key(
    _: "MessageTable", sub_msg_name: str, __: MessageTreeValue
) -> str:
    return sub_msg_name


class MessageTable(BaseTableWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(proxy_model=MessageFilterProxyModel(), parent=parent)
        self._pending_messages: list[tuple[MessageInfo, bool]] = []
        self._batch_timer = QTimer(self)
        self._batch_timer.setInterval(50)
        self._batch_timer.setSingleShot(True)
        self._batch_timer.timeout.connect(self._flush_pending_messages)
        self._unmapped_candidates_by_obf: dict[str, list[tuple[str, float]]] = {}
        columns: list[ColumnInfo] = [
            ColumnInfo(name="Heure"),
            ColumnInfo(name="Origine"),
            ColumnInfo(name="Nombre"),
            ColumnInfo(name="Type"),
            ColumnInfo(name="Contenu", is_hidden=True),
        ]
        self.table.set_columns(columns)

        header = self.table.horizontalHeader()
        assert header is not None
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)

        self.table.setColumnWidth(0, 90)
        self.table.setColumnWidth(1, 10)
        self.table.setColumnWidth(2, 80)

        self.table.setEditTriggers(TableWidget.EditTrigger.NoEditTriggers)

    @cached(cache=LRUCache[str, int](maxsize=500), key=_deep_count_fields_cache_key)
    def deep_count_fields(self, sub_msg_name: str, dico: MessageTreeValue) -> int:
        if not isinstance(dico, dict):
            return 1
        count = len(dico)
        for value in dico.values():
            if isinstance(value, dict):
                count += self.deep_count_fields(sub_msg_name, value)
            elif isinstance(value, list):
                for value_part in value:
                    count += self.deep_count_fields(sub_msg_name, value_part)
        return count

    def add_row(self, msg_info: MessageInfo, was_send_from_proxy: bool) -> None:
        self._pending_messages.append((msg_info, was_send_from_proxy))
        if not self._batch_timer.isActive():
            self._batch_timer.start()

    def _flush_pending_messages(self) -> None:
        if not self._pending_messages:
            return

        rows_to_add: list[list[QStandardItem]] = []
        for msg_info, was_send_from_proxy in self._pending_messages:
            date_field = QStandardItem(msg_info.received_time.strftime("%H:%M:%S"))
            origin_field = QStandardItem("S" if msg_info.from_server else "C")

            display_name = msg_info.sub_msg_name
            if msg_info.msg_json is None:
                candidates = self._unmapped_candidates_by_obf.get(msg_info.sub_msg_name)
                if candidates:
                    candidates_str = ", ".join(
                        f"{name} ({sim:.0%})" for name, sim in candidates
                    )
                    display_name = f"{msg_info.sub_msg_name} ? {candidates_str}"
            sub_msg_name_field = QStandardItem(display_name)

            count = ""
            if msg_info.obf_msg_json:
                count = str(
                    self.deep_count_fields(msg_info.sub_msg_name, msg_info.obf_msg_json)
                )
            elif msg_info.msg_json:
                count = str(
                    self.deep_count_fields(msg_info.sub_msg_name, msg_info.msg_json)
                )
            count_fields = QStandardItem(count)

            content_msg_field = QStandardItem("")
            content_msg_field.setData(msg_info, Qt.ItemDataRole.UserRole)

            if was_send_from_proxy:
                date_field.setData(GREEN_COLOR, Qt.ItemDataRole.BackgroundRole)
                origin_field.setData(GREEN_COLOR, Qt.ItemDataRole.BackgroundRole)
                sub_msg_name_field.setData(GREEN_COLOR, Qt.ItemDataRole.BackgroundRole)
                count_fields.setData(GREEN_COLOR, Qt.ItemDataRole.BackgroundRole)

            rows_to_add.append(
                [
                    date_field,
                    origin_field,
                    count_fields,
                    sub_msg_name_field,
                    content_msg_field,
                ]
            )

        self.table.item_model.append_rows(rows_to_add)
        self._pending_messages.clear()
