from d3_mapping.resources.protos.game.common_pb2 import ObjectItemInventory
from data_center.data_reader import DataReader
from data_center.i18n import I18N
from PyQt5.QtCore import QSize, pyqtSlot
from PyQt5.QtWidgets import QListWidgetItem, QVBoxLayout, QWidget
from qfluentwidgets import ListWidget, SmoothMode

from src.bot import Bot
from src.gui.utils.profiling import profiled_slot

CARD_WIDTH = 150
CARD_HEIGHT = 80


class InventoryTab(QWidget):
    def __init__(self, bot: Bot):
        super().__init__()
        self.setLayout(QVBoxLayout())
        self.bot = bot
        self.list_item_by_uid: dict[int, QListWidgetItem] = {}

        self.list_widget = ListWidget()
        self.list_widget.scrollDelegate.verticalSmoothScroll.setSmoothMode(
            SmoothMode.NO_SMOOTH
        )
        self.list_widget.setViewMode(ListWidget.IconMode)
        self.list_widget.setResizeMode(ListWidget.Adjust)
        self.list_widget.setMovement(ListWidget.Static)
        self.list_widget.setSpacing(10)
        self.list_widget.setUniformItemSizes(True)
        self.list_widget.setGridSize(QSize(CARD_WIDTH, CARD_HEIGHT))

        self.list_widget.setStyleSheet(
            "QListWidget { background-color: transparent; border: none; }"
        )

        self.layout().addWidget(self.list_widget)

        self.bot.inventory_signals.added_object_item.connect(
            profiled_slot(self.on_added_object_item)
        )
        self.bot.inventory_signals.updated_object_item.connect(
            profiled_slot(self.on_updated_object_item)
        )
        self.bot.inventory_signals.deleted_object_item_uid.connect(
            profiled_slot(self.on_deleted_object_item_uid)
        )
        self.bot.inventory_signals.clear_inventory.connect(
            profiled_slot(self.on_clear_inventory)
        )

    @pyqtSlot(ObjectItemInventory)
    def on_added_object_item(self, object_item: ObjectItemInventory):
        list_item = QListWidgetItem(self.list_widget)
        list_item.setSizeHint(QSize(CARD_WIDTH, CARD_HEIGHT))
        list_item.setText(self.get_item_widget_text(object_item))
        self.list_widget.addItem(list_item)
        self.list_item_by_uid[object_item.item.uid] = list_item

    @pyqtSlot(int)
    def on_deleted_object_item_uid(self, uid: int):
        if uid in self.list_item_by_uid:
            list_item = self.list_item_by_uid[uid]
            row = self.list_widget.row(list_item)
            self.list_widget.takeItem(row)
            del self.list_item_by_uid[uid]

    @pyqtSlot(ObjectItemInventory)
    def on_updated_object_item(self, object_item: ObjectItemInventory):
        self.list_item_by_uid[object_item.item.uid].setText(
            self.get_item_widget_text(object_item)
        )

    @pyqtSlot()
    def on_clear_inventory(self):
        self.list_widget.clear()
        self.list_item_by_uid.clear()

    def get_item_widget_text(self, object_item: ObjectItemInventory):
        item_data = DataReader().item_by_id.get(object_item.item.gid)
        if item_data and item_data.nameId:
            item_name = I18N().name_by_id.get(
                item_data.nameId, f"Item {object_item.item.gid}"
            )
        else:
            item_name = f"Item {object_item.item.gid}"
        item_name = item_name
        return f"{item_name} \n\n {object_item.item.quantity}"
