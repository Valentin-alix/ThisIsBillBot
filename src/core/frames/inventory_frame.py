from dataclasses import dataclass

from d3_mapping.resources.protos.game.common_pb2 import ExchangeType
from d3_mapping.resources.protos.game.dialog_pb2 import DialogLeaveRequest
from d3_mapping.resources.protos.game.exchange_pb2 import (
    ExchangeLeaveEvent,
    ExchangeStartedWithStorageEvent,
)
from d3_mapping.resources.protos.game.inventory_pb2 import (
    InventoryWeightEvent,
    InventoryContentEvent,
    KamasUpdateEvent,
    ObjectAddedEvent,
    ObjectQuantityEvent,
    ObjectDeletedEvent,
    ObjectsDeletedEvent,
    ObjectsAddedEvent,
    ObjectsQuantityEvent,
    StorageInventoryContentEvent,
    StorageObjectRemovedEvent,
    StorageObjectUpdateEvent,
)
from src.core.frames.frame import Frame


@dataclass
class InventoryFrame(Frame):
    def __post_init__(self):
        self.game_info_signals.disconnected.connect(
            self.game_state.inventory.clear_state
        )
        self.event_manager.on(
            InventoryWeightEvent,
            self.on_inventory_weight_event,
            originator=self,
        )
        self.event_manager.on(
            InventoryContentEvent, self.on_inventory_content_event, originator=self
        )
        self.event_manager.on(
            ObjectsDeletedEvent, self.on_objects_deleted_event, originator=self
        )
        self.event_manager.on(
            ObjectDeletedEvent, self.on_object_deleted_event, originator=self
        )
        self.event_manager.on(
            ObjectQuantityEvent, self.on_object_quantity_event, originator=self
        )
        self.event_manager.on(
            ObjectsQuantityEvent, self.on_objects_quantity_event, originator=self
        )
        self.event_manager.on(
            ObjectAddedEvent, self.on_object_added_event, originator=self
        )
        self.event_manager.on(
            ObjectsAddedEvent, self.on_objects_added_event, originator=self
        )
        self.event_manager.before(
            DialogLeaveRequest, self.before_dialog_leave_request, originator=self
        )
        self.event_manager.on(
            InventoryContentEvent, self.on_inventoy_content_event, originator=self
        )
        self.event_manager.on(
            ExchangeStartedWithStorageEvent,
            self.on_exchange_started_with_storage_event,
            originator=self,
        )
        self.event_manager.on(
            KamasUpdateEvent, self.on_kamas_update_event, originator=self
        )

    def on_inventory_weight_event(self, message: InventoryWeightEvent):
        self.game_state.inventory.inventory_weight = message.inventory_weight
        self.game_state.inventory.weight_max = message.weight_max

    def on_inventory_content_event(self, msg: InventoryContentEvent):
        self.game_state.inventory.objects_by_uid = {
            object.item.uid: object for object in msg.objects
        }

    def on_object_added_event(self, msg: ObjectAddedEvent):
        self.game_state.inventory.objects_by_uid[msg.object.item.uid] = msg.object

    def on_objects_added_event(self, msg: ObjectsAddedEvent):
        for object in msg.objects:
            self.game_state.inventory.objects_by_uid[object.item.uid] = object

    def on_object_quantity_event(self, msg: ObjectQuantityEvent):
        if msg.object.object_uid in self.game_state.inventory.objects_by_uid:
            self.game_state.inventory.objects_by_uid[
                msg.object.object_uid
            ].item.quantity = msg.object.quantity
        else:
            print(
                f"Did not found {msg.object.object_uid} in inventory after objectQuantiyEvent"
            )

    def on_objects_quantity_event(self, msg: ObjectsQuantityEvent):
        for object in msg.object:
            if object.object_uid in self.game_state.inventory.objects_by_uid:
                self.game_state.inventory.objects_by_uid[
                    object.object_uid
                ].item.quantity = object.quantity
            else:
                print(
                    f"Did not found {object.object_uid} in inventory after objectsQuantiyEvent"
                )

    def on_object_deleted_event(self, msg: ObjectDeletedEvent):
        if msg.object_uid in self.game_state.inventory.objects_by_uid:
            del self.game_state.inventory.objects_by_uid[msg.object_uid]
        else:
            print(f"Did not found {msg.object_uid} in inventory after objectDeleted")

    def on_objects_deleted_event(self, msg: ObjectsDeletedEvent):
        for object_uid in msg.objects_uid:
            if object_uid in self.game_state.inventory.objects_by_uid:
                del self.game_state.inventory.objects_by_uid[object_uid]
            else:
                print(f"Did not found {object_uid} in inventory after objectDeleted")

    def before_dialog_leave_request(self, msg: DialogLeaveRequest):
        if self.is_playing_event.is_set():
            return None
        return msg

    def on_exchange_started_with_storage_event(
        self, msg: ExchangeStartedWithStorageEvent
    ):
        if not msg.exchange_type == ExchangeType.BANK:
            return
        self.logger.info("Exchange started with bank")
        self.event_manager.on(
            StorageInventoryContentEvent,
            self.on_storage_inventory_content_event_bank,
            originator=self,
            once=True,
        )
        self.event_manager.on(
            StorageObjectUpdateEvent,
            self.on_storage_object_update_event,
            originator=self,
        )
        self.event_manager.on(
            StorageObjectRemovedEvent,
            self.on_storage_object_removed_event,
            originator=self,
        )
        self.event_manager.on(
            ExchangeLeaveEvent,
            self.on_exchange_leave_storage_event,
            originator=self,
            once=True,
        )

    def on_storage_inventory_content_event_bank(
        self, msg: StorageInventoryContentEvent
    ):
        self.game_state.inventory.bank_object_by_gid = {
            item.item.gid: item for item in msg.objects
        }

    def on_storage_object_update_event(self, msg: StorageObjectUpdateEvent):
        self.game_state.inventory.bank_object_by_gid[msg.object.item.gid] = msg.object

    def on_storage_object_removed_event(self, msg: StorageObjectRemovedEvent):
        related_gid = next(
            (
                gid
                for gid, object in self.game_state.inventory.bank_object_by_gid.items()
                if object.item.uid == msg.object_uid
            ),
            None,
        )
        if not related_gid:
            return self.logger.info("Did not found related gid in chest, skip.")

        self.game_state.inventory.bank_object_by_gid.pop(related_gid)

    def on_exchange_leave_storage_event(self, msg: ExchangeLeaveEvent):
        self.logger.info("Leaving storage")
        self.event_manager.clear_listener_by_origin_and_type(
            StorageObjectRemovedEvent, self
        )
        self.event_manager.clear_listener_by_origin_and_type(
            StorageObjectUpdateEvent, self
        )
        self.event_manager.clear_listener_by_origin_and_type(
            StorageInventoryContentEvent, self
        )

    def on_inventoy_content_event(self, msg: InventoryContentEvent):
        self.game_state.inventory.kamas = msg.kamas

    def on_kamas_update_event(self, msg: KamasUpdateEvent):
        self.game_state.inventory.kamas = msg.quantity
