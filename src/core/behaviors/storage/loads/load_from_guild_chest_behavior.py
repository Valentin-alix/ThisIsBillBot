from dataclasses import dataclass
from functools import partial

from dofus_unity_reader.data_center.data_reader import DataReader
from dofus_unity_reader.data_center.i18n import I18N
from datas.protos.non_obf.game.exchange_pb2 import (
    ExchangeLeaveEvent,
    ExchangeObjectMoveRequest,
)
from datas.protos.non_obf.game.guild_chest_pb2 import (
    GuildChestCurrentListenersAddEvent,
    GuildChestTabSelectRequest,
)
from datas.protos.non_obf.game.inventory_pb2 import (
    InventoryWeightEvent,
)

from src.core.behaviors.dialog_handler_behavior import DialogHandlerBehavior
from src.core.behaviors.storage.enter_chests.enter_guild_chest_behavior import (
    EnterGuildChestBehavior,
)
from src.core.behaviors.storage.unloads.unload_behavior import UnloadBehavior
from src.core.config import BASE_RANGE, SMALL_RANGE, USEFUL_UNLOAD
from src.core.states.guild_chest_state import GuildChestState


@dataclass
class LoadItemInfo:
    item_gid: int
    remaining_quantity: int
    tab: int

    def __str__(self):
        name_id = DataReader().item_by_id[self.item_gid].nameId
        name = I18N().name_by_id.get(name_id, f"Unknown {self.item_gid}")
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
    ) -> None:
        if error_code is not None:
            return self.finish(error_code)
        self.on_unloaded(load_items_infos)

    def on_unloaded(self, load_items_infos: list[LoadItemInfo]) -> None:
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
    ) -> None:
        if error_code is not None:
            return self.finish(error_code=error_code, load_items_infos=load_items_infos)
        self.load_item(load_items_infos)

    def load_item(self, load_items_infos: list[LoadItemInfo]) -> None:
        if len(load_items_infos) == 0:
            self.event_manager.on(
                ExchangeLeaveEvent,
                callback=lambda _: self.finish(load_items_infos=load_items_infos),
                originator=self,
                once=True,
                override_on_self=True,
            )
            return self.run_timer(BASE_RANGE, self.leave_all_dialogs)

        load_item_info = load_items_infos[0]
        if load_item_info.tab != self.game_state.guild_chest.tab_number:
            return self.go_to_tab(load_item_info.tab, load_items_infos)

        available_quantity = GuildChestState.get_available_quantity(
            self.game_state.player.server_id,
            load_item_info.tab,
            load_item_info.item_gid,
        )

        if available_quantity == 0:
            load_items_infos.remove(load_item_info)
            return self.load_item(load_items_infos)

        related_item = GuildChestState.get_item_by_gid(
            self.game_state.player.server_id,
            load_item_info.tab,
            load_item_info.item_gid,
        )

        if related_item is None:
            load_items_infos.remove(load_item_info)
            return self.load_item(load_items_infos)

        quantity_to_unload = min(load_item_info.remaining_quantity, available_quantity)
        if quantity_to_unload == 0:
            load_items_infos.remove(load_item_info)
            return self.load_item(load_items_infos)

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
                override_on_self=True,
            )
            return self.run_timer(BASE_RANGE, self.leave_all_dialogs)

        valid_quantity = min(portable_quantity, quantity_to_unload)

        GuildChestState.reserve_quantity(
            self.game_state.player.server_id,
            load_item_info.tab,
            load_item_info.item_gid,
            valid_quantity,
            self.game_state.player.character_name,
        )

        load_item_info.remaining_quantity -= valid_quantity
        if load_item_info.remaining_quantity < 100:
            load_items_infos.remove(load_item_info)

        self.event_manager.on(
            InventoryWeightEvent,
            callback=lambda _: self.on_item_loaded(
                load_item_info.tab,
                load_item_info.item_gid,
                valid_quantity,
                load_items_infos,
            ),
            originator=self,
            once=True,
            override_on_self=True,
        )
        req = ExchangeObjectMoveRequest(
            object_uid=related_item.item.uid,
            quantity=-valid_quantity,
        )
        self.send_message_delayed(req, SMALL_RANGE)

    def go_to_tab(self, tab_number: int, load_items_infos: list[LoadItemInfo]) -> None:
        self.event_manager.on(
            GuildChestCurrentListenersAddEvent,
            lambda _: self.load_item(load_items_infos=load_items_infos),
            once=True,
            originator=self,
            override_on_self=True,
        )
        return self.run_timer(
            SMALL_RANGE,
            lambda: self.event_manager.send(
                GuildChestTabSelectRequest(tab_number=tab_number)
            ),
        )

    def on_item_loaded(
        self, tab: int, gid: int, quantity: int, load_items_infos: list[LoadItemInfo]
    ) -> None:
        GuildChestState.release_reservation(
            self.game_state.player.server_id,
            tab,
            gid,
            quantity,
            self.game_state.player.character_name,
        )
        self.load_item(load_items_infos)

    def leave_all_dialogs(self) -> None:
        self.leave_dialog()

    def clear_behavior(self) -> None:
        GuildChestState.clear_all_reservations_for_bot(
            self.game_state.player.server_id,
            self.game_state.player.character_name,
        )
        super().clear_behavior()
