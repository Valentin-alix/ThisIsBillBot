from dataclasses import dataclass, field
from functools import partial

from datas.protos.non_obf.game.exchange_pb2 import (
    ExchangeObjectMoveRequest,
)
from datas.protos.non_obf.game.inventory_pb2 import (
    InventoryWeightEvent,
)

from src.core.behaviors.recovery import RecoverableBehavior
from src.core.behaviors.storage.enter_chests.enter_bank_chest_behavior import (
    EnterBankChestBehavior,
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
class LoadFromBankBehavior(RecoverableBehavior):
    enter_bank_behavior: EnterBankChestBehavior
    unload_behavior: UnloadBehavior
    _pending_load_items: list[PendingLoadItem] = field(init=False, default_factory=lambda: [])

    def run(self, load_items_infos: list[LoadItemInfo], unload_first: bool = True) -> None:
        self.init_recovery_listeners()
        self.ensure_free_to_act(
            lambda: self.start_bank_load(load_items_infos=load_items_infos, unload_first=unload_first)
        )

    def start_bank_load(self, load_items_infos: list[LoadItemInfo], unload_first: bool = True) -> None:
        self._pending_load_items = [
            PendingLoadItem.from_request(load_item_info) for load_item_info in load_items_infos
        ]
        if unload_first and self.game_state.inventory.pod_percentage > USEFUL_UNLOAD:
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
            return self.finish(error_code, load_items_infos=[])
        self.on_unloaded()

    def on_unloaded(self) -> None:
        self.run_timer(
            HumanTimingsService().get_timing_base_action(),
            lambda: self.enter_bank_behavior.start(
                callback=self.on_entered_bank_behavior,
                parent=self,
            ),
        )

    def on_entered_bank_behavior(
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
        related_item = self.game_state.inventory.get_bank_object_by_gid(current_load.item_gid)
        if related_item is None:
            self._pending_load_items.pop(0)
            return self.on_item_loaded()

        quantity_to_unload = min(
            current_load.remaining_quantity,
            related_item.item.quantity,
        )
        if quantity_to_unload == 0:
            self._pending_load_items.pop(0)
            return self.on_item_loaded()

        portable_quantity = get_portable_quantity(
            self.game_state,
            current_load.item_gid,
        )
        if portable_quantity == 0:
            return self.on_all_loaded()

        valid_quantity = min(portable_quantity, quantity_to_unload)
        current_load.remaining_quantity -= valid_quantity
        if current_load.remaining_quantity < 100:
            self._pending_load_items.pop(0)

        self.event_manager.on(
            InventoryWeightEvent,
            callback=lambda _: self.on_item_loaded(),
            originator=self,
            once=True,
            override_on_self=True,
        )
        req = ExchangeObjectMoveRequest(
            object_uid=related_item.item.uid,
            quantity=-valid_quantity,
        )
        self.send_message_delayed(
            req,
            HumanTimingsService().get_timing_between_bank_transfers(),
        )

    def on_all_loaded(self) -> None:
        self.run_timer(
            HumanTimingsService().get_timing_before_bank_close(),
            lambda: self.finish(load_items_infos=self._build_remaining_requests()),
        )

    def on_item_loaded(self) -> None:
        self.load_item()

    def _build_remaining_requests(self) -> list[LoadItemInfo]:
        return [load_item.to_request() for load_item in self._pending_load_items]
