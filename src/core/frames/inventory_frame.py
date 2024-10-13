from dataclasses import dataclass

from d3_mapping.resources.protos.game.dialog_pb2 import DialogLeaveRequest
from d3_mapping.resources.protos.game.inventory_pb2 import (
    InventoryWeightEvent,
    InventoryContentEvent,
    ObjectAddedEvent,
    ObjectQuantityEvent,
    ObjectDeletedEvent,
    ObjectsDeletedEvent,
    ObjectsAddedEvent,
    ObjectsQuantityEvent,
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
        self.game_state.inventory.objects_by_uid[
            msg.object.object_uid
        ].item.quantity = msg.object.quantity

    def on_objects_quantity_event(self, msg: ObjectsQuantityEvent):
        for object in msg.object:
            self.game_state.inventory.objects_by_uid[
                object.object_uid
            ].item.quantity = object.quantity

    def on_object_deleted_event(self, msg: ObjectDeletedEvent):
        del self.game_state.inventory.objects_by_uid[msg.object_uid]

    def on_objects_deleted_event(self, msg: ObjectsDeletedEvent):
        for object_uid in msg.objects_uid:
            del self.game_state.inventory.objects_by_uid[object_uid]

    def before_dialog_leave_request(self, msg: DialogLeaveRequest):
        if self.is_playing_event.is_set():
            return None
        return msg
