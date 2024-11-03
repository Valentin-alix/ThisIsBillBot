from dataclasses import dataclass

from d3_mapping.resources.protos.game.common_pb2 import DialogType
from d3_mapping.resources.protos.game.dialog_pb2 import (
    DialogLeaveRequest,
)
from d3_mapping.resources.protos.game.exchange_pb2 import (
    ExchangeLeaveEvent,
    ExchangeObjectTransferAllFromInventoryRequest,
)
from d3_mapping.resources.protos.game.inventory_pb2 import (
    InventoryWeightEvent,
)

from src.controller.human_timings import HumanTimingsController
from src.core.behaviors.behavior import Behavior
from src.core.behaviors.movements.auto_trip.auto_trip_smart_behavior import (
    AutoTripSmartBehavior,
)
from src.core.behaviors.npcs.npc_dialog_behavior import NpcDialogBehavior
from src.core.behaviors.storage.enter_chests.enter_bank_chest_behavior import (
    EnterBankChestBehavior,
)
from src.core.config.storage import USEFUL_UNLOAD
from src.core.config.timings import BEFORE_CLOSING_INVENTORY
from src.exceptions import UnexpectedStateException


@dataclass
class UnloadInBankBehavior(Behavior):
    npc_dialog_behavior: NpcDialogBehavior
    auto_trip_world_behavior: AutoTripSmartBehavior
    enter_bank_chest_behavior: EnterBankChestBehavior

    def run(self):
        if self.game_state.inventory.pod_percentage < USEFUL_UNLOAD:
            return self.finish()

        self.enter_bank_chest_behavior.start(
            callback=self.on_enter_bank_chest_behavior, parent=self
        )

    def on_enter_bank_chest_behavior(self, error_code: str | None):
        if error_code is not None:
            return self.finish()

        self.event_manager.on(
            InventoryWeightEvent,
            callback=self.on_inventory_weight_event,
            originator=self,
            once=True,
            timeout=30,
            on_timeout=self.leave_all_dialogs,
        )
        request = ExchangeObjectTransferAllFromInventoryRequest()
        self.run_timer(
            HumanTimingsController().get_timing_unload_on_bank(),
            lambda: self.event_manager.send(request),
        )

    def on_inventory_weight_event(self, msg: InventoryWeightEvent):
        self.run_timer(BEFORE_CLOSING_INVENTORY, self.leave_all_dialogs)

    def leave_all_dialogs(self):
        self.event_manager.on(
            ExchangeLeaveEvent,
            callback=self.on_exchange_leave_event,
            originator=self,
            once=True,
        )
        request = DialogLeaveRequest()
        self.event_manager.send(request)

    def on_exchange_leave_event(self, msg: ExchangeLeaveEvent):
        if msg.dialog_type != DialogType.DIALOG_EXCHANGE:
            raise UnexpectedStateException(msg.dialog_type)
        self.finish()
