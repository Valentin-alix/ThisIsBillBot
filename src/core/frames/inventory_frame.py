from dataclasses import dataclass

from d3_mapping.resources.protos.game.exchange_pb2 import (
    ExchangeLeaveEvent,
    ExchangeObjectMovePricedRequest,
    ExchangeObjectMoveRequest,
    ExchangeObjectTransferAllFromInventoryRequest,
    ExchangeStartedWithStorageEvent,
)
from d3_mapping.resources.protos.game.inventory_pb2 import (
    InventoryContentEvent,
    ObjectAddedEvent,
    ObjectQuantityEvent,
    ObjectsAddedEvent,
    StorageInventoryContentEvent,
)

from src.core.frames.frame import Frame


@dataclass
class InventoryFrame(Frame):
    def __post_init__(self):
        self.game_info_signals.disconnected.connect(
            self.game_state.inventory.clear_state
        )
        self.event_manager.on(
            ExchangeObjectTransferAllFromInventoryRequest,
            self.on_exchange_object_transfer_all_from_inventory_request,
            originator=self,
        )
        self.event_manager.on(
            InventoryContentEvent,
            self.on_inventory_content_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            ExchangeStartedWithStorageEvent,
            self.on_exchange_started_with_storage_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            ObjectAddedEvent,
            self.on_object_added_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            ObjectsAddedEvent,
            self.on_objects_added_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            ObjectQuantityEvent,
            self.on_object_quantity_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            ExchangeObjectMovePricedRequest,
            self.on_exchange_object_move_priced_request,
            originator=self,
            priority=self.priority,
        )

    def on_exchange_object_move_priced_request(
        self, message: ExchangeObjectMovePricedRequest
    ):
        self.on_move_object_inventory(message.object_uid, message.quantity, None)

    def on_object_quantity_event(self, message: ObjectQuantityEvent):
        self.game_state.inventory.objects_by_uid[
            message.object.object_uid
        ].item.quantity = message.object.quantity
        self.inventory_signals.updated_object_item.emit(
            self.game_state.inventory.objects_by_uid[message.object.object_uid]
        )

    def on_inventory_content_event(self, msg: InventoryContentEvent):
        self.game_state.inventory.objects_by_uid.clear()
        for object in msg.objects:
            self.game_state.inventory.objects_by_uid[object.item.uid] = object
        self.game_state.inventory.kamas = msg.kamas

    def on_exchange_object_transfer_all_from_inventory_request(
        self, msg: ExchangeObjectTransferAllFromInventoryRequest
    ):
        self.game_state.inventory.objects_by_uid.clear()

    def on_object_added_event(self, msg: ObjectAddedEvent):
        self.game_state.inventory.objects_by_uid[msg.object.item.uid] = msg.object

    def on_objects_added_event(self, msg: ObjectsAddedEvent):
        for object in msg.objects:
            self.game_state.inventory.objects_by_uid[object.item.uid] = object

    def on_exchange_started_with_storage_event(
        self, msg: ExchangeStartedWithStorageEvent
    ):
        if msg.storage_max_slot <= 10_000:
            return
        self.logger.info("Exchange started with bank")
        self.event_manager.on(
            StorageInventoryContentEvent,
            self.on_storage_inventory_content_event_bank,
            originator=self,
            once=True,
            priority=self.priority,
        )
        self.event_manager.on(
            ExchangeObjectMoveRequest,
            self.on_exchange_move_request_on_bank,
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

    def on_storage_inventory_content_event_bank(
        self, msg: StorageInventoryContentEvent
    ):
        self.game_state.inventory.bank_object_by_gid = {
            item.item.gid: item for item in msg.objects
        }
        self.logger.info(
            f"bank object by gid : {list(self.game_state.inventory.bank_object_by_gid.keys())}"
        )

    def on_exchange_move_request_on_bank(self, msg: ExchangeObjectMoveRequest):
        bank_item = next(
            (
                item
                for item in self.game_state.inventory.bank_object_by_gid.values()
                if item.item.uid == msg.object_uid
            ),
            None,
        )
        if bank_item is not None:
            bank_item.item.quantity += msg.quantity
            assert bank_item.item.quantity >= 0
            if bank_item.item.quantity == 0:
                self.game_state.inventory.bank_object_by_gid.pop(bank_item.item.gid)

        self.on_move_object_inventory(
            msg.object_uid, msg.quantity, bank_item.item.gid if bank_item else None
        )

    def on_exchange_leave_storage_event(self, msg: ExchangeLeaveEvent):
        self.logger.info("Leaving storage")
        self.event_manager.clear_listener_by_origin_and_type(
            ExchangeObjectMoveRequest, self
        )
        self.event_manager.clear_listener_by_origin_and_type(
            StorageInventoryContentEvent, self
        )

    def on_move_object_inventory(self, object_uid: int, quantity: int, gid: int | None):
        inventory_item = self.game_state.inventory.objects_by_uid.get(object_uid)
        if not inventory_item:
            assert gid is not None
            inventory_item = next(
                (
                    object
                    for object in self.game_state.inventory.objects_by_uid.values()
                    if object.item.gid == gid
                ),
                None,
            )
            if not inventory_item:
                # handled by object added
                return

        if inventory_item.item.quantity - quantity == 0:
            self.game_state.inventory.objects_by_uid.pop(inventory_item.item.uid)
