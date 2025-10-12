from dataclasses import dataclass, field
from functools import partial

from DBDofusUnity.datas.protos.non_obf.game.exchange_pb2 import (
    ExchangeObjectMoveRequest,
)
from DBDofusUnity.datas.protos.non_obf.game.guild_chest_pb2 import (
    GuildChestCurrentListenersAddEvent,
    GuildChestTabSelectRequest,
)
from DBDofusUnity.datas.protos.non_obf.game.inventory_pb2 import (
    InventoryWeightEvent,
)
from src.core.behaviors.recovery_behavior import RecoverableBehavior
from src.core.behaviors.storage.enter_chests.enter_guild_chest_behavior import (
    EnterGuildChestBehavior,
)
from src.core.behaviors.storage.loads.load_item_request import (
    LoadItemInfo,
    PendingLoadItem,
    get_portable_quantity,
)
from src.core.behaviors.storage.unloads.unload_behavior import UnloadBehavior
from src.core.config import USEFUL_UNLOAD
from src.services.human_timings import HumanTimingsService


@dataclass
class LoadFromGuildChestBehavior(RecoverableBehavior):
    enter_guild_chest_behavior: EnterGuildChestBehavior
    unload_behavior: UnloadBehavior
    _pending_load_items: list[PendingLoadItem] = field(init=False, default_factory=lambda: [])

    def run(self, load_items_infos: list[LoadItemInfo]) -> None:
        self.init_recovery_listeners()
        self.ensure_free_to_act(lambda: self.start_guild_chest_load(load_items_infos=load_items_infos))

    def start_guild_chest_load(self, load_items_infos: list[LoadItemInfo]) -> None:
        self._pending_load_items = [
            PendingLoadItem.from_request(load_item_info) for load_item_info in load_items_infos
        ]
        if self.game_state.inventory.pod_percentage > USEFUL_UNLOAD:
            return self.unload_behavior.start(
                callback=partial(
                    self.on_unload_behavior_finished,
                ),
                parent=self,
            )
        self.on_unloaded()

    def on_unload_behavior_finished(
        self,
        error_code: str | None,
    ) -> None:
        if error_code is not None:
            return self.finish(error_code)
        self.on_unloaded()

    def on_unloaded(self) -> None:
        self.run_timer(
            HumanTimingsService().get_timing_base_action(),
            lambda: self.enter_guild_chest_behavior.start(
                callback=self.on_entered_guild_chest_behavior,
                parent=self,
            ),
        )

    def on_entered_guild_chest_behavior(
        self,
        error_code: str | None,
    ) -> None:
        if error_code is not None:
            return self.finish(
                error_code=error_code,
                load_items_infos=self._build_remaining_requests(),
            )
        self.load_item()

    def load_item(self) -> None:
        if len(self._pending_load_items) == 0:
            return self.on_all_loaded()

        current_load = self._pending_load_items[0]
        if current_load.tab != self.game_state.guild_chest.tab_number:
            return self.go_to_tab(current_load.tab)

        storage = self.game_state.guild_chest.storage
        available_quantity = storage.get_available_quantity(
            current_load.tab,
            current_load.item_gid,
        )

        if available_quantity == 0:
            self._pending_load_items.pop(0)
            return self.load_item()

        related_item = storage.get_item_by_gid(
            current_load.tab,
            current_load.item_gid,
        )

        if related_item is None:
            self._pending_load_items.pop(0)
            return self.load_item()

        quantity_to_unload = min(current_load.remaining_quantity, available_quantity)
        if quantity_to_unload == 0:
            self._pending_load_items.pop(0)
            return self.load_item()

        portable_quantity = get_portable_quantity(
            self.game_state,
            current_load.item_gid,
        )
        if portable_quantity == 0:
            return self.on_all_loaded()

        valid_quantity = min(portable_quantity, quantity_to_unload)

        storage.reserve_quantity(
            current_load.tab,
            current_load.item_gid,
            valid_quantity,
            self.game_state.player.character_name,
        )

        current_load.remaining_quantity -= valid_quantity
        if current_load.remaining_quantity < 100:
            self._pending_load_items.pop(0)

        self.event_manager.on(
            InventoryWeightEvent,
            callback=lambda _: self.on_item_loaded(
                current_load.tab,
                current_load.item_gid,
                valid_quantity,
            ),
            originator=self,
            once=True,
            override_on_self=True,
        )
        req = ExchangeObjectMoveRequest(
            object_uid=related_item.item.uid,
            quantity=-valid_quantity,
        )
        self.send_message_delayed(req, HumanTimingsService().get_timing_short_action())

    def go_to_tab(self, tab_number: int) -> None:
        self.event_manager.on(
            GuildChestCurrentListenersAddEvent,
            lambda _: self.load_item(),
            once=True,
            originator=self,
            override_on_self=True,
        )
        return self.run_timer(
            HumanTimingsService().get_timing_short_action(),
            lambda: self.event_manager.send(GuildChestTabSelectRequest(tab_number=tab_number)),
        )

    def on_item_loaded(self, tab: int, gid: int, quantity: int) -> None:
        self.game_state.guild_chest.storage.release_reservation(
            tab,
            gid,
            quantity,
            self.game_state.player.character_name,
        )
        self.load_item()

    def _build_remaining_requests(self) -> list[LoadItemInfo]:
        return [load_item.to_request() for load_item in self._pending_load_items]

    def on_all_loaded(self) -> None:
        self.run_timer(
            HumanTimingsService().get_timing_base_action(),
            lambda: self.finish(load_items_infos=self._build_remaining_requests()),
        )

    def clear_behavior(self) -> None:
        self.game_state.guild_chest.storage.clear_all_reservations_for_bot(
            self.game_state.player.character_name,
        )
        super().clear_behavior()
