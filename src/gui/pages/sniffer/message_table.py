from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItem, QColor
from PyQt5.QtWidgets import QHeaderView
from qfluentwidgets import TableWidget

from src.gui.components.table.column_info import ColumnInfo
from src.gui.components.table.table import BaseTableWidget
from src.interfaces.models.message import MessageInfo


class MessageTable(BaseTableWidget):
    def __init__(self) -> None:
        super().__init__()
        columns: list[ColumnInfo] = [
            ColumnInfo(name="Heure"),
            ColumnInfo(name="Serveur"),
            ColumnInfo(name="Type"),
            ColumnInfo(name="Message"),
            ColumnInfo(name="Contenu", is_hidden=True),
        ]
        self.table.set_columns(columns)

        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)

        self.table.setEditTriggers(TableWidget.NoEditTriggers)

    def add_row(self, msg_info: MessageInfo, was_send_from_proxy: bool):
        model = self.table.item_model

        date_field = QStandardItem(msg_info.received_time.strftime("%H:%M:%S.%f"))
        server_type_field = QStandardItem(msg_info.server_type)
        msg_name_field = QStandardItem(msg_info.msg_name)
        sub_msg_name_field = QStandardItem(msg_info.sub_msg_name)
        content_msg_field = QStandardItem(str(msg_info))
        content_msg_field.setData(msg_info, Qt.UserRole)

        if was_send_from_proxy:
            date_field.setData(QColor("green"), Qt.BackgroundRole)
            server_type_field.setData(QColor("green"), Qt.BackgroundRole)
            msg_name_field.setData(QColor("green"), Qt.BackgroundRole)
            sub_msg_name_field.setData(QColor("green"), Qt.BackgroundRole)

        model.append_row(
            [
                date_field,
                server_type_field,
                msg_name_field,
                sub_msg_name_field,
                content_msg_field,
            ]
        )
