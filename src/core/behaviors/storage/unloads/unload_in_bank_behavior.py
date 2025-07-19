from dataclasses import dataclass
from functools import partial

from datas.protos.non_obf.game.common_pb2 import ObjectItemInventory
from datas.protos.non_obf.game.exchange_pb2 import (
    ExchangeLeaveEvent,
    ExchangeObjectMoveRequest,
)
from datas.protos.non_obf.game.inventory_pb2 import (
    InventoryWeightEvent,
)

from src.core.behaviors.dialog_handler_behavior import DialogHandlerBehavior
from src.core.behaviors.movements.auto_trip.auto_trip_smart_behavior import (
    AutoTripSmartBehavior,
)
from src.core.behaviors.storage.enter_chests.enter_bank_chest_behavior import (
    EnterBankChestBehavior,
)
from src.core.config import (
    BEFORE_CLOSING_INVENTORY,
    SMALL_RANGE,
    USEFUL_UNLOAD,
)
from src.core.engine.items.item_formatter import format_item_name


@dataclass
class UnloadInBankBehavior(DialogHandlerBehavior):
    auto_trip_world_behavior: AutoTripSmartBehavior
    enter_bank_chest_behavior: EnterBankChestBehavior

    def run(self) -> None:
        if self.game_state.inventory.pod_percentage < USEFUL_UNLOAD:
            self.logger.info(
                f"Pod usage {self.game_state.inventory.pod_percentage}% below threshold {USEFUL_UNLOAD}%, skipping unload"
            )
            return self.finish()

        self.logger.info(
            f"Starting bank unload (pods: {self.game_state.inventory.pod_percentage}%)"
        )
        self.enter_bank_chest_behavior.start(
            callback=self.on_enter_bank_chest_behavior, parent=self
        )

    def on_enter_bank_chest_behavior(self, error_code: str | None) -> None:
        if error_code is not None:
            self.logger.error(f"Failed to enter bank: {error_code}")
            return self.finish(error_code)

        self.logger.info("Transferring all items to bank")
        object_to_unloads = self.game_state.inventory.get_unlinked_objects()
        self.unload_object(object_to_unloads)

    def unload_object(self, object_to_unloads: list[ObjectItemInventory]) -> None:
        if len(object_to_unloads) == 0:
            return self.run_timer(
                BEFORE_CLOSING_INVENTORY,
                lambda: self.leave_dialog(
                    on_leave_callback=self.on_exchange_leave_event
                ),
            )

        self.event_manager.on(
            InventoryWeightEvent,
            partial(
                self.on_inventory_weight_event, object_to_unloads=object_to_unloads
            ),
            originator=self,
            once=True,
            override_on_self=True,
        )
        next_object = object_to_unloads.pop()
        item_name = format_item_name(next_object.item.gid)

        self.logger.info(
            f"Unloading {item_name} x{next_object.item.quantity} ({len(object_to_unloads)} remaining)"
        )
        req = ExchangeObjectMoveRequest(
            object_uid=next_object.item.uid, quantity=next_object.item.quantity
        )
        self.event_manager.send(req)

    def on_inventory_weight_event(
        self, msg: InventoryWeightEvent, object_to_unloads: list[ObjectItemInventory]
    ) -> None:
        self.run_timer(SMALL_RANGE, lambda: self.unload_object(object_to_unloads))

    def on_exchange_leave_event(self, msg: ExchangeLeaveEvent) -> None:
        self.logger.info("Bank unload completed successfully")
        self.finish()
