from datetime import datetime

from google.protobuf.message import Message
from PyQt6.QtCore import QModelIndex, QTimer, pyqtSlot
from PyQt6.QtWidgets import QVBoxLayout, QWidget
from qfluentwidgets import TableWidget
from qfluentwidgets.components.widgets.model_combo_box import QStandardItem

from src.core.events_manager.event_manager import EventManager
from src.core.events_manager.listener import Listener
from src.gui.components.listener_details_box import ListenerDetailsBox
from src.gui.components.table.column_info import ColumnInfo
from src.gui.components.table.table import BaseTableWidget


class ListenersStatsTable(BaseTableWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        columns: list[ColumnInfo] = [
            ColumnInfo(name="Heure d'enregistrement"),
            ColumnInfo(name="Origine"),
            ColumnInfo(name="Message type"),
        ]
        self.table.set_columns(columns)
        self.table.setEditTriggers(TableWidget.EditTrigger.NoEditTriggers)
        self.listener_to_row: dict[Listener[Message], int] = {}


class ListenersStatsWidget(QWidget):
    def __init__(self, event_manager: EventManager, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.event_manager = event_manager

        layout = QVBoxLayout()
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(8)
        self.setLayout(layout)

        self.stats_table = ListenersStatsTable(self)
        self.stats_table.table.setSelectionMode(TableWidget.SelectionMode.SingleSelection)
        self.stats_table.table.clicked.connect(self.on_row_double_clicked)
        layout.addWidget(self.stats_table)

        self.sorted_listeners: list[Listener[Message]] = []

        self.event_manager.signals.listeners_added.connect(self.on_listeners_added)
        self.event_manager.signals.listeners_removed.connect(self.on_listeners_removed)

        self._rebuild_timer = QTimer(self)
        self._rebuild_timer.setInterval(50)
        self._rebuild_timer.setSingleShot(True)
        self._rebuild_timer.timeout.connect(self.init)

        self.init()

    def init(self) -> None:
        self.stats_table.listener_to_row.clear()
        self.stats_table.table.item_model.clear_all()
        self.sorted_listeners.clear()

        all_listeners: list[Listener[Message]] = []
        for listeners in self.event_manager.listeners_by_type_msg.values():
            all_listeners.extend(listeners)

        self.sorted_listeners = sorted(all_listeners, key=self.get_sort_key)

        for row_index, listener in enumerate(self.sorted_listeners):
            self.add_listener_at_index(listener, row_index)

    def get_sort_key(self, listener: Listener[Message]) -> tuple[datetime, str]:
        return (
            listener.registered_at,
            listener.originator.__class__.__name__,
        )

    def add_listener_at_index(self, listener: Listener[Message], row_index: int) -> None:
        timestamp_str = listener.registered_at.strftime("%H:%M:%S.%f")[:-3]
        originator_str = listener.originator.__class__.__name__
        type_str = listener.msg_type.__name__

        timestamp_item = QStandardItem(timestamp_str)
        originator_item = QStandardItem(originator_str)
        type_item = QStandardItem(type_str)

        model = self.stats_table.table.item_model
        model.beginInsertRows(QModelIndex(), row_index, row_index)
        model._data.insert(row_index, [timestamp_item, originator_item, type_item])
        model.endInsertRows()

        self.stats_table.listener_to_row[listener] = row_index

        for listener_obj, old_row in list(self.stats_table.listener_to_row.items()):
            if old_row >= row_index and listener_obj != listener:
                self.stats_table.listener_to_row[listener_obj] = old_row + 1

    @pyqtSlot(list)
    def on_listeners_added(self, added_listeners: list[Listener[Message]]) -> None:
        if added_listeners:
            self._schedule_rebuild()

    @pyqtSlot(list)
    def on_listeners_removed(self, removed_listeners: list[Listener[Message]]) -> None:
        if removed_listeners:
            self._schedule_rebuild()

    def _schedule_rebuild(self) -> None:
        if not self._rebuild_timer.isActive():
            self._rebuild_timer.start()

    def on_row_double_clicked(self, proxy_index: QModelIndex) -> None:
        source_index = self.stats_table.table.proxy_model.mapToSource(proxy_index)
        row = source_index.row()

        for listener, listener_row in self.stats_table.listener_to_row.items():
            if listener_row == row:
                dialog = ListenerDetailsBox(listener, self)
                dialog.exec()
                break
