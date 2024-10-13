from dataclasses import dataclass
from functools import partial

from d3_mapping.resources.protos.game.dialog_pb2 import DialogLeaveRequest
from d3_mapping.resources.protos.game.exchange_pb2 import (
    ExchangeLeaveEvent,
    ExchangeObjectMoveRequest,
)
from d3_mapping.resources.protos.game.inventory_pb2 import InventoryWeightEvent
from data_center.data_reader import DataReader
from src.const import BASE_RANGE, SMALL_RANGE
from src.core.behaviors.behavior import Behavior
from src.core.behaviors.storage.consts import USEFUL_UNLOAD
from src.core.behaviors.storage.enter_bank_chest_behavior import EnterBankChestBehavior
from src.core.behaviors.storage.load_from_guild_chest_behavior import LoadItemInfo
from src.core.behaviors.storage.unload_behavior import UnloadBehavior
from src.exceptions import UnhandledErrorCodeException


@dataclass
class LoadFromBankBehavior(Behavior):
    enter_bank_behavior: EnterBankChestBehavior
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
            raise UnhandledErrorCodeException(error_code)
        self.on_unloaded(load_items_infos)

    def on_unloaded(self, load_items_infos: list[LoadItemInfo]):
        self.run_timer(
            BASE_RANGE,
            lambda: self.enter_bank_behavior.start(
                callback=partial(
                    self.on_entered_bank_behavior,
                    load_items_infos=load_items_infos,
                ),
                parent=self,
            ),
        )

    def on_entered_bank_behavior(
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
            return self.leave_all_dialogs()

        load_item_info = load_items_infos[0]
        related_item = self.game_state.inventory.bank_object_by_gid.get(
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
        ) // (DataReader().item_by_id[load_item_info.item_gid].realWeight or 0)
        if portable_quantity == 0:
            self.event_manager.on(
                ExchangeLeaveEvent,
                callback=lambda _: self.finish(load_items_infos=load_items_infos),
                originator=self,
                once=True,
            )
            return self.leave_all_dialogs()

        valid_quantity = min(portable_quantity, quantity_to_unload)
        load_item_info.remaining_quantity -= valid_quantity
        related_item.item.quantity -= valid_quantity
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
        self.run_timer(SMALL_RANGE, lambda: self.event_manager.send(req))

    def on_item_loaded(self, load_items_infos: list[LoadItemInfo]):
        self.load_item(load_items_infos)

    def leave_all_dialogs(self):
        request = DialogLeaveRequest()
        self.event_manager.send(request)
        self.event_manager.send(request)
