from typing import Any
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItem, QColor
from PyQt5.QtWidgets import QHeaderView
from qfluentwidgets import TableWidget

from d3_mapping.gui.component.table.column_info import ColumnInfo
from d3_mapping.gui.component.table.table import BaseTableWidget
from d3_mapping.models.message import MessageInfo


class MessageTable(BaseTableWidget):
    def __init__(self) -> None:
        super().__init__()
        columns: list[ColumnInfo] = [
            ColumnInfo(name="Heure"),
            ColumnInfo(name="Origine"),
            ColumnInfo(name="Type"),
            ColumnInfo(name="Contenu", is_hidden=True),
        ]
        self.table.set_columns(columns)

        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)

        self.table.setEditTriggers(TableWidget.NoEditTriggers)

    def add_row(self, msg_info: MessageInfo, was_send_from_proxy: bool):
        model = self.table.item_model

        date_field = QStandardItem(msg_info.received_time.strftime("%H:%M:%S.%f"))
        origin_field = QStandardItem("Serveur" if msg_info.from_server else "Client")
        sub_msg_name_field = QStandardItem(msg_info.sub_msg_name)

        def flatten_json(_json: dict | list | Any, parent_key="", sep="."):
            human_value: str = ""
            if isinstance(_json, dict):
                for sub_key, sub_value in _json.items():
                    human_value += f" {flatten_json(sub_value, sub_key, sep=sep)}"
            elif isinstance(_json, list):
                for sub_index, sub_value in enumerate(_json):
                    human_value += (
                        f" {flatten_json(sub_value, str(sub_index), sep=sep)}"
                    )
            else:
                human_value += f" {parent_key} = {_json}"
            return human_value

        content_msg_field = QStandardItem(flatten_json(msg_info.msg_json))
        content_msg_field.setData(msg_info, Qt.UserRole)

        if was_send_from_proxy:
            date_field.setData(QColor("green"), Qt.BackgroundRole)
            origin_field.setData(QColor("green"), Qt.BackgroundRole)
            sub_msg_name_field.setData(QColor("green"), Qt.BackgroundRole)

        model.append_row(
            [
                date_field,
                origin_field,
                sub_msg_name_field,
                content_msg_field,
            ]
        )
