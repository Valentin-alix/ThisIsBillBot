from dataclasses import dataclass

from protos.game.common_pb2 import DialogType
from protos.game.dialog_pb2 import DialogLeaveRequest
from protos.game.exchange_pb2 import (
    ExchangeObjectTransferAllFromInventoryRequest,
    ExchangeLeaveEvent,
)
from protos.game.inventory_pb2 import (
    InventoryWeightEvent,
)
from src.const import ON_OPENED_INVENTORY, BEFORE_CLOSING_INVENTORY
from src.core.behaviors.behavior import Behavior
from src.core.behaviors.movements.auto_trip.auto_trip_smart_behavior import (
    AutoTripSmartBehavior,
)
from src.core.behaviors.npc_dialog_behavior import NpcDialogBehavior
from src.core.behaviors.storage.consts import USEFUL_UNLOAD
from src.core.behaviors.storage.enter_bank_chest_behavior import EnterBankChestBehavior
from src.exceptions import UnhandledErrorCodeException, UnexpectedStateException


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
            raise UnhandledErrorCodeException(error_code)
        self.event_manager.on(
            InventoryWeightEvent,
            callback=self.on_inventory_weight_event,
            originator=self,
            once=True,
            timeout=20,
            on_timeout=self.leave_all_dialogs,
        )
        request = ExchangeObjectTransferAllFromInventoryRequest()
        self.run_timer(ON_OPENED_INVENTORY, lambda: self.event_manager.send(request))

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
        self.event_manager.send(request)

    def on_exchange_leave_event(self, msg: ExchangeLeaveEvent):
        if msg.dialog_type != DialogType.DIALOG_EXCHANGE:
            raise UnexpectedStateException(msg.dialog_type)
        self.finish()
