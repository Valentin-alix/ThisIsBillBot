from dataclasses import dataclass

from D3Database.data_center.data_reader import DataReader
from D3Database.data_center.i18n import I18N
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
from src.const import STRICT_MODE
from src.core.frames.frame import Frame
from src.core.states.guild_chest_state import GuildChestState


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
        GuildChestState.set_tab_content(
            self.game_state.player.server_id,
            self.game_state.guild_chest.tab_number,
            list(msg.objects),
        )
        self.logger.info(
            f"New storage for tab number : {self.game_state.guild_chest.tab_number}"
        )

    def on_exchange_move_request_on_guild_chest(self, msg: ExchangeObjectMoveRequest):
        GuildChestState.update_item_quantity(
            self.game_state.player.server_id,
            self.game_state.guild_chest.tab_number,
            msg.object_uid,
            msg.quantity,
        )
        inventory_item = self.game_state.inventory.objects_by_uid.get(msg.object_uid)
        if inventory_item is not None:
            inventory_item.item.quantity -= msg.quantity
            if inventory_item.item.quantity < 0:
                error = f"item {I18N().name_by_id[DataReader().item_by_id[inventory_item.item.gid].nameId]} quantity is {inventory_item.item.quantity}"
                if STRICT_MODE:
                    raise ValueError(error)
                self.logger.error(error)

            if inventory_item.item.quantity <= 0:
                self.game_state.inventory.objects_by_uid.pop(inventory_item.item.uid)

    def on_exchange_leave_guild_chest_event(self, msg: ExchangeLeaveEvent):
        self.unregister_listener(ExchangeObjectMoveRequest)
        self.unregister_listener(StorageInventoryContentEvent)

    def on_guild_members_ship_event(self, msg: GuildMembershipEvent):
        self.game_state.guild_chest.has_guild = True
        self.game_state.guild_chest.rank_id = msg.rank_id
