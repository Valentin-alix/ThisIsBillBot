from dataclasses import dataclass

from D3Mapping.d3_mapping.resources.protos.game.common_pb2 import DialogType
from D3Mapping.d3_mapping.resources.protos.game.exchange_pb2 import (
    ExchangeLeaveEvent,
    ExchangeObjectTransferAllFromInventoryRequest,
)
from D3Mapping.d3_mapping.resources.protos.game.inventory_pb2 import (
    InventoryWeightEvent,
)
from src.core.behaviors.dialog_handler_behavior import DialogHandlerBehavior
from src.core.behaviors.movements.auto_trip.auto_trip_smart_behavior import (
    AutoTripSmartBehavior,
)
from src.core.behaviors.storage.enter_chests.enter_bank_chest_behavior import (
    EnterBankChestBehavior,
)
from src.core.config import BEFORE_CLOSING_INVENTORY, USEFUL_UNLOAD
from src.exceptions import UnexpectedStateException
from src.services.human_timings import HumanTimingsService


@dataclass
class UnloadInBankBehavior(DialogHandlerBehavior):
    auto_trip_world_behavior: AutoTripSmartBehavior
    enter_bank_chest_behavior: EnterBankChestBehavior

    def run(self):
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

    def on_enter_bank_chest_behavior(self, error_code: str | None):
        if error_code is not None:
            self.logger.error(f"Failed to enter bank: {error_code}")
            return self.finish()

        self.logger.info("Transferring all items to bank")
        self.event_manager.on(
            InventoryWeightEvent,
            callback=self.on_inventory_weight_event,
            originator=self,
            once=True,
            timeout=30,
            on_timeout=lambda: self.leave_dialog(
                on_leave_callback=self.on_exchange_leave_event
            ),
        )
        request = ExchangeObjectTransferAllFromInventoryRequest()
        self.run_timer(
            HumanTimingsService().get_timing_unload_on_bank(),
            lambda: self.event_manager.send(request),
        )

    def on_inventory_weight_event(self, msg: InventoryWeightEvent):
        self.logger.info(
            f"Transfer complete, new pod usage: {self.game_state.inventory.pod_percentage}%"
        )
        self.run_timer(
            BEFORE_CLOSING_INVENTORY,
            lambda: self.leave_dialog(on_leave_callback=self.on_exchange_leave_event),
        )

    def on_exchange_leave_event(self, msg: ExchangeLeaveEvent):
        if msg.dialog_type != DialogType.DIALOG_EXCHANGE:
            raise UnexpectedStateException(msg.dialog_type)
        self.logger.info("Bank unload completed successfully")
        self.finish()
