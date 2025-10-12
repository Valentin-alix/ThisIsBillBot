from dataclasses import dataclass

from DBDofusUnity.datas.protos.non_obf.game.exchange_pb2 import (
    ExchangeObjectTransferAllFromInventoryRequest,
)
from DBDofusUnity.datas.protos.non_obf.game.inventory_pb2 import (
    InventoryWeightEvent,
)
from src.core.behaviors.movements.auto_trip.auto_trip_smart_behavior import (
    AutoTripSmartBehavior,
)
from src.core.behaviors.recovery_behavior import RecoverableBehavior
from src.core.behaviors.storage.enter_chests.enter_bank_chest_behavior import (
    EnterBankChestBehavior,
)
from src.core.config import USEFUL_UNLOAD
from src.services.human_timings import HumanTimingsService

TRANSFER_ALL_TIMEOUT_SECONDS = 15.0


@dataclass
class UnloadInBankBehavior(RecoverableBehavior):
    auto_trip_world_behavior: AutoTripSmartBehavior
    enter_bank_chest_behavior: EnterBankChestBehavior

    def run(self) -> None:
        self.init_recovery_listeners()
        self.ensure_free_to_act(lambda: self.start_bank_unload())

    def start_bank_unload(self) -> None:
        if self.game_state.inventory.pod_percentage < USEFUL_UNLOAD:
            self.logger.info(
                f"Pod usage {self.game_state.inventory.pod_percentage}% below threshold {USEFUL_UNLOAD}%, skipping unload"
            )
            return self.finish()

        self.logger.info(f"Starting bank unload (pods: {self.game_state.inventory.pod_percentage}%)")
        self.enter_bank_chest_behavior.start(callback=self.on_enter_bank_chest_behavior, parent=self)

    def on_enter_bank_chest_behavior(self, error_code: str | None) -> None:
        if error_code is not None:
            self.logger.error(f"Failed to enter bank: {error_code}")
            return self.finish(error_code)

        if not self.game_state.inventory.get_unlinked_objects():
            self.logger.info("Nothing transferable in the bag, leaving the chest open")
            return self.on_unloaded()

        self.logger.info("Transferring all items to bank")
        self.run_timer(
            HumanTimingsService().get_timing_unload_on_bank(),
            self.transfer_all_to_bank,
        )

    def transfer_all_to_bank(self) -> None:
        self.event_manager.on(
            InventoryWeightEvent,
            self.on_inventory_weight_event,
            originator=self,
            once=True,
            timeout=TRANSFER_ALL_TIMEOUT_SECONDS,
            on_timeout=self.on_transfer_all_timeout,
        )
        self.event_manager.send(ExchangeObjectTransferAllFromInventoryRequest())

    def on_inventory_weight_event(self, msg: InventoryWeightEvent) -> None:
        self.logger.info(f"Bag transferred, inventory weight is now {msg.inventory_weight}")
        self.on_unloaded()

    def on_transfer_all_timeout(self) -> None:
        self.logger.warning("No inventory update after the transfer request, giving up on it")
        self.on_unloaded()

    def on_unloaded(self) -> None:
        self.logger.info("Bank unload completed successfully")
        self.run_timer(HumanTimingsService().get_timing_before_bank_close(), self.finish)
