from dataclasses import dataclass

from protos.game.exchange_pb2 import (
    ExchangeStartedWithMultiTabStorageEvent,
    ExchangeLeaveEvent,
)
from protos.game.inventory_pb2 import (
    StorageInventoryContentEvent,
    StorageObjectUpdateEvent,
    StorageObjectRemovedEvent,
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
        )

    def on_exchange_started_with_multi_tab_storage_event(
        self, msg: ExchangeStartedWithMultiTabStorageEvent
    ):
        self.game_state.guild_chest.tab_number = msg.tab_number
        self.event_manager.on(
            StorageInventoryContentEvent,
            callback=self.on_storage_inventory_content_after_tab_storage,
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
            self.on_exchange_leave_guild_chest_event,
            originator=self,
            once=True,
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

    def on_storage_object_removed_event(self, msg: StorageObjectRemovedEvent):
        related_gid = next(
            (
                gid
                for gid, object in CHEST_OBJECT_BY_GID_BY_TAB[
                    self.game_state.guild_chest.tab_number
                ].items()
                if object.item.uid == msg.object_uid
            ),
            None,
        )
        if not related_gid:
            return self.logger.info("Did not found related git in chest, skip.")

        CHEST_OBJECT_BY_GID_BY_TAB[self.game_state.guild_chest.tab_number].pop(
            related_gid
        )

    def on_exchange_leave_guild_chest_event(self, msg: ExchangeLeaveEvent):
        self.event_manager.clear_listener_by_origin_and_type(
            StorageObjectRemovedEvent, self
        )
        self.event_manager.clear_listener_by_origin_and_type(
            StorageObjectUpdateEvent, self
        )
