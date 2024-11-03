from dataclasses import dataclass

from d3_mapping.resources.protos.game.dialog_pb2 import DialogLeaveRequest
from d3_mapping.resources.protos.game.exchange_pb2 import (
    ExchangeLeaveEvent,
    ExchangeMoveKamaRequest,
    ExchangeObjectMoveRequest,
    ExchangeObjectTransferAllFromInventoryRequest,
    ExchangeStartedWithStorageEvent,
)
from d3_mapping.resources.protos.game.inventory_pb2 import (
    InventoryContentEvent,
    InventoryWeightEvent,
    ObjectAddedEvent,
    ObjectsAddedEvent,
    StorageInventoryContentEvent,
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
            priority=self.priority,
        )
        self.event_manager.on(
            ExchangeObjectTransferAllFromInventoryRequest,
            self.on_exchange_object_transfer_all_from_inventory_request,
            originator=self,
        )
        self.event_manager.before(
            DialogLeaveRequest,
            self.before_dialog_leave_request,
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
            ExchangeMoveKamaRequest,
            self.on_exchange_move_kama_request,
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

    def on_inventory_weight_event(self, message: InventoryWeightEvent):
        self.game_state.inventory.inventory_weight = message.inventory_weight
        self.game_state.inventory.weight_max = message.weight_max

    def on_inventory_content_event(self, msg: InventoryContentEvent):
        self.game_state.inventory.objects_by_uid.clear()
        for object in msg.objects:
            self.game_state.inventory.objects_by_uid[object.item.uid] = object
        self.game_state.inventory.kamas = msg.kamas

    def on_exchange_object_transfer_all_from_inventory_request(
        self, msg: ExchangeObjectTransferAllFromInventoryRequest
    ):
        self.game_state.inventory.objects_by_uid.clear()

    def before_dialog_leave_request(self, msg: DialogLeaveRequest):
        if self.is_playing_event.is_set():
            self.logger.info("Cancel dialog leave request from client")
            return None
        return msg

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
            StorageObjectUpdateEvent,
            self.on_storage_object_update_event,
            originator=self,
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

    def on_storage_object_update_event(self, msg: StorageObjectUpdateEvent):
        self.game_state.inventory.bank_object_by_gid[msg.object.item.gid] = msg.object

    def on_exchange_move_request_on_bank(self, msg: ExchangeObjectMoveRequest):
        bank_item = next(
            (
                item
                for item in self.game_state.inventory.bank_object_by_gid.values()
                if item.item.uid == msg.object_uid
            ),
            None,
        )
        inventory_item = self.game_state.inventory.objects_by_uid.get(msg.object_uid)

        if bank_item is not None and bank_item.item.quantity == 0:
            # the quantity is already updated in load from bank behavior
            self.game_state.inventory.bank_object_by_gid.pop(bank_item.item.gid)

        if inventory_item is not None:
            self.logger.info(
                f"Inventory item {inventory_item.item.gid} with quantity {inventory_item.item.quantity}"
            )
            inventory_item.item.quantity -= msg.quantity
            assert inventory_item.item.quantity >= 0
            if inventory_item.item.quantity == 0:
                self.game_state.inventory.objects_by_uid.pop(inventory_item.item.uid)

    def on_exchange_leave_storage_event(self, msg: ExchangeLeaveEvent):
        self.logger.info("Leaving storage")
        self.event_manager.clear_listener_by_origin_and_type(
            ExchangeObjectMoveRequest, self
        )
        self.event_manager.clear_listener_by_origin_and_type(
            StorageObjectUpdateEvent, self
        )
        self.event_manager.clear_listener_by_origin_and_type(
            StorageInventoryContentEvent, self
        )

    def on_exchange_move_kama_request(self, msg: ExchangeMoveKamaRequest):
        self.game_state.inventory.kamas += msg.quantity
