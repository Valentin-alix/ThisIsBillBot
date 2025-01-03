from typing import Iterable, override

from datas.protos.non_obf.game.common_pb2 import (
    ObjectItemInventory,
)
from datas.protos.non_obf.game.exchange_pb2 import (
    ExchangeStartedWithStorageEvent,
)

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
        self.game_state.inventory.bank_object_by_gid = {
            item.item.gid: item for item in objects
        }
        self.game_state.inventory.inventory_signals.bank_refreshed.emit(objects)

    @override
    def set_object(self, object_item_inventory: ObjectItemInventory):
        self.game_state.inventory.bank_object_by_gid[object_item_inventory.item.gid] = (
            object_item_inventory
        )
        self.game_state.inventory.inventory_signals.bank_item_updated.emit(
            object_item_inventory
        )

    @override
    def remove_object(self, uid: int):
        gid_to_delete: int | None = None
        for gid, object_item in self.game_state.inventory.bank_object_by_gid.items():
            if object_item.item.uid == uid:
                gid_to_delete = gid
        if gid_to_delete is None:
            raise ValueError(f"{uid} not found in bank storage")
        del self.game_state.inventory.bank_object_by_gid[gid_to_delete]
        self.game_state.inventory.inventory_signals.bank_item_removed.emit(uid)
