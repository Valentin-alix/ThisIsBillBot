from abc import ABC, abstractmethod
from collections.abc import Iterable

from DBDofusUnity.datas.protos.non_obf.game.common_pb2 import (
    ObjectItemInventory,
)
from DBDofusUnity.datas.protos.non_obf.game.exchange_pb2 import (
    ExchangeLeaveEvent,
)
from DBDofusUnity.datas.protos.non_obf.game.inventory_pb2 import (
    StorageInventoryContentEvent,
    StorageObjectRemovedEvent,
    StorageObjectsRemovedEvent,
    StorageObjectsUpdateEvent,
    StorageObjectUpdateEvent,
)

from src.core.frames.frame import Frame


class MixinStorage(Frame, ABC):
    def on_opened_storage(self):
        self.event_manager.on(
            StorageInventoryContentEvent,
            self.on_storage_inventory_content_event,
            originator=self,
            once=True,
            priority=self.priority,
        )
        self.event_manager.on(
            StorageObjectUpdateEvent,
            self.on_storage_object_update_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            StorageObjectsUpdateEvent,
            self.on_storage_objects_update_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            StorageObjectRemovedEvent,
            self.on_storage_object_removed_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            StorageObjectsRemovedEvent,
            self.on_storage_objects_removed_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            ExchangeLeaveEvent,
            self.on_exchange_leave_storage_event,
            originator=self,
            once=True,
            priority=self.priority,
        )

    @abstractmethod
    def set_objects(self, objects_item_inventory: Iterable[ObjectItemInventory]): ...

    @abstractmethod
    def set_object(self, object_item_inventory: ObjectItemInventory): ...

    @abstractmethod
    def remove_object(self, uid: int): ...

    def on_storage_inventory_content_event(self, msg: StorageInventoryContentEvent):
        self.set_objects(msg.objects)
        self.logger.info(f"storage object by gid : {list(msg.objects)}")

    def on_storage_object_update_event(self, msg: StorageObjectUpdateEvent):
        self.set_object(msg.object)

    def on_storage_objects_update_event(self, msg: StorageObjectsUpdateEvent):
        for item in msg.objects:
            self.set_object(item)

    def on_storage_object_removed_event(self, msg: StorageObjectRemovedEvent):
        self.remove_object(msg.object_uid)

    def on_storage_objects_removed_event(self, msg: StorageObjectsRemovedEvent):
        for uid in msg.objects_uid:
            self.remove_object(uid)

    def on_exchange_leave_storage_event(self, msg: ExchangeLeaveEvent):
        self.logger.info("Leaving storage")
        self.unregister_listener(StorageInventoryContentEvent)
        self.unregister_listener(StorageObjectUpdateEvent)
        self.unregister_listener(StorageObjectsUpdateEvent)
        self.unregister_listener(StorageObjectRemovedEvent)
        self.unregister_listener(StorageObjectsRemovedEvent)
