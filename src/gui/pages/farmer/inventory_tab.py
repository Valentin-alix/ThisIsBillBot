from datas.protos.non_obf.game.common_pb2 import (
    ObjectItemInventory,
)
from dofus_unity_reader.data_center.data_reader import DataReader
from dofus_unity_reader.data_center.i18n import I18N
from PyQt6.QtCore import QSize, QTimer, pyqtSlot
from PyQt6.QtWidgets import QListView, QListWidgetItem, QVBoxLayout, QWidget
from qfluentwidgets import ListWidget, SmoothMode

from src.core.bot.bot import Bot

CARD_WIDTH = 150
CARD_HEIGHT = 120


class InventoryTab(QWidget):
    def __init__(self, bot: Bot, parent: QWidget | None = None):
        super().__init__(parent=parent)
        self.bot = bot
        self.items_by_uid: dict[int, ObjectItemInventory] = {}
        self.list_item_by_uid: dict[int, QListWidgetItem] = {}
        self.signals_connected = False
        self._rebuild_timer = QTimer(self)
        self._rebuild_timer.setInterval(50)
        self._rebuild_timer.setSingleShot(True)
        self._rebuild_timer.timeout.connect(self._rebuild_sorted_list)

        self.list_widget = ListWidget(self)
        self.list_widget.scrollDelegate.verticalSmoothScroll.setSmoothMode(
            SmoothMode.NO_SMOOTH
        )
        self.list_widget.setViewMode(QListView.ViewMode.IconMode)
        self.list_widget.setResizeMode(QListView.ResizeMode.Adjust)
        self.list_widget.setMovement(QListView.Movement.Static)
        self.list_widget.setSpacing(10)
        self.list_widget.setUniformItemSizes(True)
        self.list_widget.setGridSize(QSize(CARD_WIDTH, CARD_HEIGHT))

        self.list_widget.setStyleSheet(
            "QListWidget { background-color: transparent; border: none; }"
        )

        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(self.list_widget)

    @pyqtSlot(ObjectItemInventory)
    def on_added_object_item(self, object_item: ObjectItemInventory):
        self.items_by_uid[object_item.item.uid] = object_item
        self._schedule_rebuild()

    @pyqtSlot(list)
    def on_added_object_items_batch(self, objects: list[ObjectItemInventory]):
        for object_item in objects:
            self.items_by_uid[object_item.item.uid] = object_item
        self._schedule_rebuild()

    @pyqtSlot(int)
    def on_deleted_object_item_uid(self, uid: int):
        if uid not in self.items_by_uid:
            return
        del self.items_by_uid[uid]
        self._schedule_rebuild()

    @pyqtSlot(ObjectItemInventory)
    def on_updated_object_item(self, object_item: ObjectItemInventory):
        if object_item.item.uid not in self.items_by_uid:
            return
        self.items_by_uid[object_item.item.uid] = object_item
        self._schedule_rebuild()

    @pyqtSlot()
    def on_clear_inventory(self):
        self.items_by_uid.clear()
        self._rebuild_timer.stop()
        self.list_widget.clear()
        self.list_item_by_uid.clear()

    def _schedule_rebuild(self) -> None:
        if not self._rebuild_timer.isActive():
            self._rebuild_timer.start()

    def _rebuild_sorted_list(self) -> None:
        self.list_widget.setUpdatesEnabled(False)
        self.list_widget.clear()
        self.list_item_by_uid.clear()
        sorted_items = sorted(
            self.items_by_uid.values(), key=lambda obj: obj.item.quantity, reverse=True
        )
        for object_item in sorted_items:
            list_item = QListWidgetItem()
            list_item.setSizeHint(QSize(CARD_WIDTH, CARD_HEIGHT))
            list_item.setText(self._get_item_text(object_item))
            self.list_widget.addItem(list_item)
            self.list_item_by_uid[object_item.item.uid] = list_item
        self.list_widget.setUpdatesEnabled(True)

    def _get_item_text(self, object_item: ObjectItemInventory) -> str:
        item_data = DataReader().item_by_id.get(object_item.item.gid)
        if item_data and item_data.nameId:
            item_name = I18N().name_by_id.get(
                item_data.nameId, f"Item {object_item.item.gid}"
            )
        else:
            item_name = f"Item {object_item.item.gid}"
        return f"{item_name} \n\n Pos : {object_item.position} \n\n {object_item.item.quantity}"

    def connect_signals(self) -> None:
        if self.signals_connected:
            return
        self.bot.inventory_signals.added_object_item.connect(self.on_added_object_item)
        self.bot.inventory_signals.added_object_items_batch.connect(
            self.on_added_object_items_batch
        )
        self.bot.inventory_signals.updated_object_item.connect(
            self.on_updated_object_item
        )
        self.bot.inventory_signals.deleted_object_item_uid.connect(
            self.on_deleted_object_item_uid
        )
        self.bot.inventory_signals.clear_inventory.connect(self.on_clear_inventory)
        self.signals_connected = True
        self._resync_inventory()

    def disconnect_signals(self) -> None:
        if not self.signals_connected:
            return
        self.bot.inventory_signals.added_object_item.disconnect(
            self.on_added_object_item
        )
        self.bot.inventory_signals.added_object_items_batch.disconnect(
            self.on_added_object_items_batch
        )
        self.bot.inventory_signals.updated_object_item.disconnect(
            self.on_updated_object_item
        )
        self.bot.inventory_signals.deleted_object_item_uid.disconnect(
            self.on_deleted_object_item_uid
        )
        self.bot.inventory_signals.clear_inventory.disconnect(self.on_clear_inventory)
        self.signals_connected = False
        self.items_by_uid.clear()
        self._rebuild_timer.stop()
        self.list_widget.clear()
        self.list_item_by_uid.clear()

    def _resync_inventory(self) -> None:
        self.items_by_uid.clear()
        self.list_widget.clear()
        self.list_item_by_uid.clear()
        inventory_items = list(self.bot.game_state.inventory.objects_by_uid.values())
        if inventory_items:
            self.on_added_object_items_batch(inventory_items)
