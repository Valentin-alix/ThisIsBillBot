from collections.abc import Iterable
from dataclasses import dataclass
from typing import override

from datas.protos.non_obf.game.common_pb2 import (
    ObjectItemInventory,
)
from datas.protos.non_obf.game.exchange_pb2 import (
    ExchangeStartedWithMultiTabStorageEvent,
)
from datas.protos.non_obf.game.guild_member_pb2 import (
    GuildMembershipEvent,
)
from datas.protos.non_obf.game.inventory_pb2 import (
    MultiTabStorageEvent,
)

from src.core.frames.mixin_storage import MixinStorage
from dofus_unity_reader.game_constants.guild import UNBOUNDED_CHEST_TAB_NUMBER


@dataclass
class GuildChestFrame(MixinStorage):
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
        self.event_manager.on(
            MultiTabStorageEvent,
            self.on_multi_tab_storage_event,
            originator=self,
            priority=self.priority,
        )

    def on_exchange_started_with_multi_tab_storage_event(self, msg: ExchangeStartedWithMultiTabStorageEvent):
        if msg.tab_number == UNBOUNDED_CHEST_TAB_NUMBER:
            msg.tab_number = msg.storage_max_slot

        self.game_state.guild_chest.tab_number = msg.tab_number
        self.on_opened_storage()

    @override
    def set_objects(self, objects_item_inventory: Iterable[ObjectItemInventory]):
        self.game_state.guild_chest.storage.set_tab_content(
            self.game_state.guild_chest.tab_number,
            list(objects_item_inventory),
        )
        self.logger.info(f"New storage for tab number : {self.game_state.guild_chest.tab_number}")

    @override
    def set_object(self, object_item_inventory: ObjectItemInventory) -> None:
        self.game_state.guild_chest.storage.set_item(
            self.game_state.guild_chest.tab_number,
            object_item_inventory,
        )

    @override
    def remove_object(self, uid: int) -> None:
        self.game_state.guild_chest.storage.remove_item_by_uid(
            self.game_state.guild_chest.tab_number,
            uid,
        )

    def on_guild_members_ship_event(self, msg: GuildMembershipEvent):
        self.game_state.guild_chest.has_guild = True
        self.game_state.guild_chest.rank_id = msg.rank_id

    def on_multi_tab_storage_event(self, msg: MultiTabStorageEvent):
        self.game_state.guild_chest.tabs = [tab.tab_number for tab in msg.tabs]
