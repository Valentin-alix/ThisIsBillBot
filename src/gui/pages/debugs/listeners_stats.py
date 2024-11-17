from bisect import bisect_left

from PyQt5.QtCore import QModelIndex, pyqtSlot
from PyQt5.QtWidgets import QVBoxLayout, QWidget
from qfluentwidgets import TableWidget
from qfluentwidgets.components.widgets.model_combo_box import QStandardItem

from src.core.events_manager.event_manager import EventManager
from src.core.events_manager.listener import Listener
from src.gui.components.listener_details_box import ListenerDetailsBox
from src.gui.components.table.column_info import ColumnInfo
from src.gui.components.table.table import BaseTableWidget


class ListenersStatsTable(BaseTableWidget):
    def __init__(self) -> None:
        super().__init__()
        columns: list[ColumnInfo] = [
            ColumnInfo(name="Heure d'enregistrement"),
            ColumnInfo(name="Originator"),
            ColumnInfo(name="Message Type"),
        ]
        self.table.set_columns(columns)
        self.table.setEditTriggers(TableWidget.NoEditTriggers)
        self.listener_to_row: dict[Listener, int] = {}


class ListenersStatsWidget(QWidget):
    def __init__(self, event_manager: EventManager, *args, **kwargs):  # type: ignore
        super().__init__(*args, **kwargs)
        self.event_manager = event_manager

        layout = QVBoxLayout()
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(8)
        self.setLayout(layout)

        self.stats_table = ListenersStatsTable()
        self.stats_table.table.setSelectionMode(self.stats_table.table.SingleSelection)
        self.stats_table.table.clicked.connect(self.on_row_double_clicked)
        layout.addWidget(self.stats_table)

        self.sorted_listeners: list[Listener] = []

        self.event_manager.signals.listeners_added.connect(self.on_listeners_added)
        self.event_manager.signals.listeners_removed.connect(self.on_listeners_removed)

        self.init()

    def init(self):
        self.stats_table.listener_to_row.clear()
        self.stats_table.table.item_model.clear_all()
        self.sorted_listeners.clear()

        with self.event_manager.lock:
            all_listeners: list[Listener] = []
            for listeners in self.event_manager.listeners_by_type_msg.values():
                all_listeners.extend(listeners)

        self.sorted_listeners = sorted(all_listeners, key=self.get_sort_key)

        for row_index, listener in enumerate(self.sorted_listeners):
            self.add_listener_at_index(listener, row_index)

    def get_sort_key(self, listener: Listener) -> tuple:
        return (
            listener.registered_at,
            listener.originator.__class__.__name__,
        )

    def add_listener_at_index(self, listener: Listener, row_index: int):
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
    def on_listeners_added(self, added_listeners: list[Listener]):
        for listener in added_listeners:
            sort_key = self.get_sort_key(listener)
            keys = [
                self.get_sort_key(listener_obj)
                for listener_obj in self.sorted_listeners
            ]
            insert_index = bisect_left(keys, sort_key)

            self.sorted_listeners.insert(insert_index, listener)
            self.add_listener_at_index(listener, insert_index)

    @pyqtSlot(list)
    def on_listeners_removed(self, removed_listeners: list[Listener]):
        removed_set = set(removed_listeners)
        rows_to_remove: list[int] = []

        for listener in removed_listeners:
            if listener in self.stats_table.listener_to_row:
                row = self.stats_table.listener_to_row[listener]
                rows_to_remove.append(row)

        for row in sorted(rows_to_remove, reverse=True):
            self.stats_table.table.item_model.remove_rows(row, 1)

            for listener_obj, listener_row in list(
                self.stats_table.listener_to_row.items()
            ):
                if listener_row == row:
                    del self.stats_table.listener_to_row[listener_obj]
                elif listener_row > row:
                    self.stats_table.listener_to_row[listener_obj] = listener_row - 1

        self.sorted_listeners = [
            listener_obj
            for listener_obj in self.sorted_listeners
            if listener_obj not in removed_set
        ]

    def on_row_double_clicked(self, proxy_index):
        source_index = self.stats_table.table.proxy_model.mapToSource(proxy_index)
        row = source_index.row()

        for listener, listener_row in self.stats_table.listener_to_row.items():
            if listener_row == row:
                dialog = ListenerDetailsBox(listener, self)
                dialog.exec()
                break
