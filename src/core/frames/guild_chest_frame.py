from dataclasses import dataclass

from d3_mapping.resources.protos.game.exchange_pb2 import (
    ExchangeLeaveEvent,
    ExchangeObjectMoveRequest,
    ExchangeStartedWithMultiTabStorageEvent,
)
from d3_mapping.resources.protos.game.inventory_pb2 import (
    MultiTabStorageEvent,
    StorageInventoryContentEvent,
    StorageObjectUpdateEvent,
)

from src.core.frames.frame import Frame
from src.core.states.guild_chest_state import CHEST_OBJECT_BY_GID_BY_TAB


@dataclass
class GuildChestFrame(Frame):
    def __post_init__(self):
        self.game_info_signals.disconnected.connect(
            self.game_state.guild_chest.clear_state
        )
        self.event_manager.on(
            ExchangeStartedWithMultiTabStorageEvent,
            self.on_exchange_started_with_multi_tab_storage_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            MultiTabStorageEvent,
            self.on_multi_tab_storage_event,
            originator=self,
            priority=self.priority,
        )

    def on_multi_tab_storage_event(self, msg: MultiTabStorageEvent):
        self.game_state.guild_chest.tabs = [tab.tab_number for tab in msg.tabs]

    def on_exchange_started_with_multi_tab_storage_event(
        self, msg: ExchangeStartedWithMultiTabStorageEvent
    ):
        if msg.tab_number == 100:
            msg.tab_number = msg.storage_max_slot

        self.game_state.guild_chest.tab_number = msg.tab_number
        self.event_manager.on(
            StorageInventoryContentEvent,
            callback=self.on_storage_inventory_content_after_tab_storage,
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
            self.on_exchange_leave_guild_chest_event,
            originator=self,
            once=True,
            priority=self.priority,
        )

    def on_storage_inventory_content_after_tab_storage(
        self, msg: StorageInventoryContentEvent
    ):
        CHEST_OBJECT_BY_GID_BY_TAB[self.game_state.guild_chest.tab_number] = {
            object.item.gid: object for object in msg.objects
        }
        self.logger.info(
            f"New storage for tab number : {self.game_state.guild_chest.tab_number} : {CHEST_OBJECT_BY_GID_BY_TAB[self.game_state.guild_chest.tab_number]}"
        )

    def on_storage_object_update_event(self, msg: StorageObjectUpdateEvent):
        CHEST_OBJECT_BY_GID_BY_TAB[self.game_state.guild_chest.tab_number][
            msg.object.item.gid
        ] = msg.object

    def on_exchange_move_request_on_bank(self, msg: ExchangeObjectMoveRequest):
        guild_item = next(
            (
                item
                for item in CHEST_OBJECT_BY_GID_BY_TAB[
                    self.game_state.guild_chest.tab_number
                ].values()
                if item.item.uid == msg.object_uid
            ),
            None,
        )
        inventory_item = self.game_state.inventory.objects_by_uid.get(msg.object_uid)

        if guild_item is not None and guild_item.item.quantity == 0:
            # the quantity is already updated in load from guild chest behavior
            CHEST_OBJECT_BY_GID_BY_TAB[self.game_state.guild_chest.tab_number].pop(
                guild_item.item.gid
            )

        if inventory_item is not None:
            self.logger.info(
                f"Inventory item {inventory_item.item.gid} with quantity {inventory_item.item.quantity}"
            )
            inventory_item.item.quantity -= msg.quantity
            assert inventory_item.item.quantity >= 0
            if inventory_item.item.quantity == 0:
                self.game_state.inventory.objects_by_uid.pop(inventory_item.item.uid)

    def on_exchange_leave_guild_chest_event(self, msg: ExchangeLeaveEvent):
        self.event_manager.clear_listener_by_origin_and_type(
            StorageObjectUpdateEvent, self
        )
        self.event_manager.clear_listener_by_origin_and_type(
            StorageInventoryContentEvent, self
        )
