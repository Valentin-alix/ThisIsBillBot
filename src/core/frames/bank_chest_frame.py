from typing import Iterable, override

from datas.protos.non_obf.game.common_pb2 import (
    ObjectItemInventory,
)
from datas.protos.non_obf.game.exchange_pb2 import (
    ExchangeStartedWithStorageEvent,
)

from src import const
from src.core.frames.mixin_storage import MixinStorage


class BankChestFrame(MixinStorage):
    def __post_init__(self):
        self.event_manager.on(
            ExchangeStartedWithStorageEvent,
            self.on_exchange_started_with_storage_event,
            originator=self,
            priority=self.priority,
        )

    def on_exchange_started_with_storage_event(
        self, msg: ExchangeStartedWithStorageEvent
    ):
        if msg.storage_max_slot <= 10_000:
            return
        self.on_opened_storage()

    @override
    def set_objects(self, objects_item_inventory: Iterable[ObjectItemInventory]):
        objects = list(objects_item_inventory)
        self.game_state.inventory.bank_objects_by_uid = {
            item.item.uid: item for item in objects
        }
        if const.DEBUG:
            self.game_state.inventory.inventory_signals.bank_refreshed.emit(objects)

    @override
    def set_object(self, object_item_inventory: ObjectItemInventory):
        self.game_state.inventory.bank_objects_by_uid[
            object_item_inventory.item.uid
        ] = object_item_inventory
        if const.DEBUG:
            self.game_state.inventory.inventory_signals.bank_item_updated.emit(
                object_item_inventory
            )

    @override
    def remove_object(self, uid: int):
        if uid not in self.game_state.inventory.bank_objects_by_uid:
            raise ValueError(f"{uid} not found in bank storage")
        del self.game_state.inventory.bank_objects_by_uid[uid]
        if const.DEBUG:
            self.game_state.inventory.inventory_signals.bank_item_removed.emit(uid)
