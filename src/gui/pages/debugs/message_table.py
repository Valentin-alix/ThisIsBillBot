import json
from typing import Any

from cachetools import cached
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItem
from PyQt5.QtWidgets import QHeaderView
from qfluentwidgets import TableWidget

from D3Mapping.d3_mapping.models.message import MessageInfo
from src.gui.components.table.column_info import ColumnInfo
from src.gui.components.table.table import BaseTableWidget
from src.gui.consts import GREEN_COLOR


class MessageTable(BaseTableWidget):
    def __init__(self) -> None:
        super().__init__()
        columns: list[ColumnInfo] = [
            ColumnInfo(name="Heure"),
            ColumnInfo(name="Origine"),
            ColumnInfo(name="Nombre"),
            ColumnInfo(name="Type"),
            ColumnInfo(name="Contenu", is_hidden=True),
        ]
        self.table.set_columns(columns)

        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)

        self.table.setColumnWidth(0, 90)
        self.table.setColumnWidth(1, 10)
        self.table.setColumnWidth(2, 80)

        self.table.setEditTriggers(TableWidget.NoEditTriggers)

    @cached(cache={}, key=lambda _, sub_msg_name, __: sub_msg_name)
    def deep_count_fields(self, sub_msg_name: str, dico: Any) -> int:
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

    def add_row(self, msg_info: MessageInfo, was_send_from_proxy: bool):
        date_field = QStandardItem(msg_info.received_time.strftime("%H:%M:%S"))
        origin_field = QStandardItem("S" if msg_info.from_server else "C")
        sub_msg_name_field = QStandardItem(msg_info.sub_msg_name)

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

        content_msg_field = QStandardItem(
            json.dumps(msg_info.msg_json) + json.dumps(msg_info.obf_msg_json)
        )
        content_msg_field.setData(msg_info, Qt.UserRole)

        if was_send_from_proxy:
            date_field.setData(GREEN_COLOR, Qt.BackgroundRole)
            origin_field.setData(GREEN_COLOR, Qt.BackgroundRole)
            sub_msg_name_field.setData(GREEN_COLOR, Qt.BackgroundRole)
            count_fields.setData(GREEN_COLOR, Qt.BackgroundRole)

        self.table.append_row(
            [
                date_field,
                origin_field,
                count_fields,
                sub_msg_name_field,
                content_msg_field,
            ]
        )
