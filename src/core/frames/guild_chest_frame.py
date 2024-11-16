from dataclasses import dataclass

from D3Mapping.d3_mapping.resources.protos.game.exchange_pb2 import (
    ExchangeLeaveEvent,
    ExchangeObjectMoveRequest,
    ExchangeStartedWithMultiTabStorageEvent,
)
from D3Mapping.d3_mapping.resources.protos.game.guild_member_pb2 import (
    GuildMembershipEvent,
)
from D3Mapping.d3_mapping.resources.protos.game.inventory_pb2 import (
    StorageInventoryContentEvent,
)
from src.core.frames.frame import Frame
from src.core.states.guild_chest_state import CHEST_OBJECT_BY_GID_BY_TAB


@dataclass
class GuildChestFrame(Frame):
    def __post_init__(self):
        self.event_manager.on(
            ExchangeStartedWithMultiTabStorageEvent,
            self.on_exchange_started_with_multi_tab_storage_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            GuildMembershipEvent,
            self.on_guild_members_ship_event,
            originator=self,
            priority=self.priority,
        )

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
            ExchangeObjectMoveRequest,
            self.on_exchange_move_request_on_guild_chest,
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

    def on_exchange_move_request_on_guild_chest(self, msg: ExchangeObjectMoveRequest):
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

        if guild_item is not None:
            assert guild_item.item.quantity + msg.quantity >= 0
            guild_item.item.quantity += msg.quantity
            if guild_item.item.quantity == 0:
                CHEST_OBJECT_BY_GID_BY_TAB[self.game_state.guild_chest.tab_number].pop(
                    guild_item.item.gid
                )

        if inventory_item is not None:
            if not inventory_item.item.quantity - msg.quantity >= 0:
                self.logger.error(
                    f"invalid futur quantity ? : {inventory_item.item.quantity}"
                )
                return
            if inventory_item.item.quantity - msg.quantity == 0:
                self.game_state.inventory.objects_by_uid.pop(inventory_item.item.uid)

    def on_exchange_leave_guild_chest_event(self, msg: ExchangeLeaveEvent):
        self.event_manager.clear_listener_by_origin_and_type(
            ExchangeObjectMoveRequest, self
        )
        self.event_manager.clear_listener_by_origin_and_type(
            StorageInventoryContentEvent, self
        )

    def on_guild_members_ship_event(self, msg: GuildMembershipEvent):
        self.game_state.guild_chest.has_guild = True
