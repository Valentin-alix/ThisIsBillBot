from dataclasses import dataclass
from functools import partial

from D3Database.data_center.data_reader import DataReader
from D3Database.data_center.i18n import I18N
from D3Mapping.d3_mapping.resources.protos.game.dialog_pb2 import DialogLeaveRequest
from D3Mapping.d3_mapping.resources.protos.game.exchange_pb2 import (
    ExchangeLeaveEvent,
    ExchangeObjectMoveRequest,
)
from D3Mapping.d3_mapping.resources.protos.game.guild_chest_pb2 import (
    GuildChestCurrentListenersAddEvent,
    GuildChestTabSelectRequest,
)
from D3Mapping.d3_mapping.resources.protos.game.inventory_pb2 import (
    InventoryWeightEvent,
)
from src.core.behaviors.dialog_handler_behavior import DialogHandlerBehavior
from src.core.behaviors.storage.enter_chests.enter_guild_chest_behavior import (
    EnterGuildChestBehavior,
)
from src.core.behaviors.storage.unloads.unload_behavior import UnloadBehavior
from src.core.config import BASE_RANGE, SMALL_RANGE, USEFUL_UNLOAD
from src.core.states.guild_chest_state import CHEST_OBJECT_BY_GID_BY_TAB


@dataclass
class LoadItemInfo:
    item_gid: int
    remaining_quantity: int
    tab: int

    def __str__(self):
        name_id = DataReader().item_by_id[self.item_gid].nameId
        name = I18N().name_by_id[name_id] if name_id is not None else ""
        return f"{name} : {self.remaining_quantity}"

    def __repr__(self):
        return self.__str__()


@dataclass
class LoadFromGuildChestBehavior(DialogHandlerBehavior):
    enter_guild_chest_behavior: EnterGuildChestBehavior
    unload_behavior: UnloadBehavior

    def run(self, load_items_infos: list[LoadItemInfo]) -> None:
        if self.game_state.inventory.pod_percentage > USEFUL_UNLOAD:
            return self.unload_behavior.start(
                callback=partial(
                    self.on_unload_behavior_finished,
                    load_items_infos=load_items_infos,
                ),
                parent=self,
            )
        self.on_unloaded(load_items_infos)

    def on_unload_behavior_finished(
        self, error_code: str | None, load_items_infos: list[LoadItemInfo]
    ):
        if error_code is not None:
            return self.finish(error_code)
        self.on_unloaded(load_items_infos)

    def on_unloaded(self, load_items_infos: list[LoadItemInfo]):
        self.run_timer(
            BASE_RANGE,
            lambda: self.enter_guild_chest_behavior.start(
                callback=partial(
                    self.on_entered_guild_chest_behavior,
                    load_items_infos=load_items_infos,
                ),
                parent=self,
            ),
        )

    def on_entered_guild_chest_behavior(
        self, error_code: str | None, load_items_infos: list[LoadItemInfo]
    ):
        if error_code is not None:
            return self.finish(error_code=error_code, load_items_infos=load_items_infos)
        self.load_item(load_items_infos)

    def load_item(self, load_items_infos: list[LoadItemInfo]):
        if len(load_items_infos) == 0:
            self.event_manager.on(
                ExchangeLeaveEvent,
                callback=lambda _: self.finish(load_items_infos=load_items_infos),
                originator=self,
                once=True,
            )
            return self.run_timer(BASE_RANGE, self.leave_all_dialogs)

        load_item_info = load_items_infos[0]
        if load_item_info.tab != self.game_state.guild_chest.tab_number:
            return self.go_to_tab(load_item_info.tab, load_items_infos)

        related_item = CHEST_OBJECT_BY_GID_BY_TAB[load_item_info.tab].get(
            load_item_info.item_gid, None
        )

        if related_item is None:
            load_items_infos.remove(load_item_info)
            return self.on_item_loaded(load_items_infos)

        quantity_to_unload = min(
            load_item_info.remaining_quantity, related_item.item.quantity
        )
        if quantity_to_unload == 0:
            load_items_infos.remove(load_item_info)
            return self.on_item_loaded(load_items_infos)

        portable_quantity = (
            self.game_state.inventory.weight_max
            - self.game_state.inventory.inventory_weight
        ) // (DataReader().item_by_id[load_item_info.item_gid].realWeight or 1)
        if portable_quantity == 0:
            self.event_manager.on(
                ExchangeLeaveEvent,
                callback=lambda _: self.finish(load_items_infos=load_items_infos),
                originator=self,
                once=True,
            )
            return self.run_timer(BASE_RANGE, self.leave_all_dialogs)

        valid_quantity = min(portable_quantity, quantity_to_unload)
        load_item_info.remaining_quantity -= valid_quantity
        if load_item_info.remaining_quantity < 100:
            load_items_infos.remove(load_item_info)

        self.event_manager.on(
            InventoryWeightEvent,
            callback=lambda _: self.on_item_loaded(load_items_infos),
            originator=self,
            once=True,
        )
        req = ExchangeObjectMoveRequest(
            object_uid=related_item.item.uid,
            quantity=-valid_quantity,
        )
        self.send_message_delayed(req, SMALL_RANGE)

    def go_to_tab(self, tab_number: int, load_items_infos: list[LoadItemInfo]):
        self.event_manager.on(
            GuildChestCurrentListenersAddEvent,
            lambda _: self.load_item(load_items_infos=load_items_infos),
            once=True,
            originator=self,
        )
        return self.run_timer(
            SMALL_RANGE,
            lambda: self.event_manager.send(
                GuildChestTabSelectRequest(tab_number=tab_number)
            ),
        )

    def on_item_loaded(self, load_items_infos: list[LoadItemInfo]):
        self.load_item(load_items_infos)

    def leave_all_dialogs(self):


        self.leave_dialog()
