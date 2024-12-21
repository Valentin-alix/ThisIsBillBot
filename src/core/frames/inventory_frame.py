from dataclasses import dataclass

from datas.protos.non_obf.game.inventory_pb2 import (
    InventoryContentEvent,
    InventoryWeightEvent,
    KamasUpdateEvent,
    ObjectAddedEvent,
    ObjectDeletedEvent,
    ObjectModifiedEvent,
    ObjectQuantityEvent,
    ObjectsAddedEvent,
    ObjectsDeletedEvent,
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
            InventoryContentEvent,
            self.on_inventory_content_event,
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
            ObjectDeletedEvent,
            self.on_object_deleted_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            ObjectsDeletedEvent,
            self.on_objects_deleted_event,
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
            ObjectsQuantityEvent,
            self.on_objects_quantity_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            ObjectModifiedEvent,
            self.on_object_modified_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            KamasUpdateEvent,
            self.on_kamas_update_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            InventoryWeightEvent,
            self.on_inventory_weight_event,
            originator=self,
            priority=self.priority,
        )

    def on_object_quantity_event(self, message: ObjectQuantityEvent):
        self.game_state.inventory.objects_by_uid[
            message.object.object_uid
        ].item.quantity = message.object.quantity
        self.inventory_signals.updated_object_item.emit(
            self.game_state.inventory.objects_by_uid[message.object.object_uid]
        )

    def on_inventory_content_event(self, msg: InventoryContentEvent):
        self.game_state.inventory.set_objects(list(msg.objects))
        self.game_state.inventory.kamas = msg.kamas

    def on_object_added_event(self, msg: ObjectAddedEvent):
        self.game_state.inventory.add_object(msg.object)

    def on_objects_added_event(self, msg: ObjectsAddedEvent):
        self.game_state.inventory.add_objects(list(msg.objects))

    def on_object_deleted_event(self, msg: ObjectDeletedEvent):
        self.game_state.inventory.remove_object(msg.object_uid)

    def on_objects_deleted_event(self, msg: ObjectsDeletedEvent):
        for uid in msg.objects_uid:
            self.game_state.inventory.remove_object(uid)

    def on_kamas_update_event(self, msg: KamasUpdateEvent):
        self.game_state.inventory.kamas = msg.quantity

    def on_inventory_weight_event(self, message: InventoryWeightEvent):
        self.game_state.inventory.inventory_weight = message.inventory_weight
        self.game_state.inventory.weight_max = message.weight_max

    def on_objects_quantity_event(self, msg: ObjectsQuantityEvent):
        for object_with_quantity in msg.object:
            self.game_state.inventory.objects_by_uid[
                object_with_quantity.object_uid
            ].item.quantity = object_with_quantity.quantity
            self.inventory_signals.updated_object_item.emit(
                self.game_state.inventory.objects_by_uid[
                    object_with_quantity.object_uid
                ]
            )

    def on_object_modified_event(self, msg: ObjectModifiedEvent):
        self.game_state.inventory.objects_by_uid[msg.object.item.uid] = msg.object
        self.inventory_signals.updated_object_item.emit(msg.object)
