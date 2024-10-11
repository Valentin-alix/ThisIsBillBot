from dataclasses import dataclass

from protos.game.common_pb2 import DialogType
from protos.game.dialog_pb2 import DialogLeaveRequest
from protos.game.exchange_pb2 import (
    ExchangeObjectTransferAllFromInventoryRequest,
    ExchangeLeaveEvent,
)
from protos.game.inventory_pb2 import (
    StorageInventoryContentEvent,
    InventoryWeightEvent,
)
from src.const import ON_OPENED_INVENTORY, BEFORE_CLOSING_INVENTORY
from src.core.behaviors.bank.consts import ASTRUB_BANK_MAP, BONTA_BANK_MAP
from src.core.behaviors.behavior import Behavior
from src.core.behaviors.movements.auto_trip.auto_trip_smart_behavior import (
    AutoTripSmartBehavior,
)
from src.core.behaviors.npc_dialog_behavior import NpcDialogBehavior, NpcInfo
from src.exceptions import UnhandledErrorCodeException, UnexpectedStateException

ASTRUB_BANK_NPC_INFO = NpcInfo(
    npc_action_id=3, npc_id=-20001, npc_map_id=ASTRUB_BANK_MAP, reply_ids=[64361]
)
BONTA_BANK_NPC_INFO = NpcInfo(
    npc_action_id=3, npc_id=-20000, npc_map_id=BONTA_BANK_MAP, reply_ids=[63535]
)

BANKS_NPC_INFOS = [ASTRUB_BANK_NPC_INFO, BONTA_BANK_NPC_INFO]

USEFUL_UNLOAD = 0.25


@dataclass
class UnloadInBankBehavior(Behavior):
    npc_dialog_behavior: NpcDialogBehavior
    auto_trip_world_behavior: AutoTripSmartBehavior

    def run(self):
        if self.game_state.inventory.pod_percentage < USEFUL_UNLOAD:
            return self.finish()

        self.auto_trip_world_behavior.start(
            callback=self.on_bank_map,
            parent=self,
            map_ids={bank.npc_map_id for bank in BANKS_NPC_INFOS},
        )

    def on_bank_map(self, error_code: str | None):
        if error_code is not None:
            raise UnhandledErrorCodeException(error_code)

        self.npc_dialog_behavior.start(
            callback=self.on_npc_dialog_behavior_finished,
            parent=self,
            npc_info=next(
                bank
                for bank in BANKS_NPC_INFOS
                if bank.npc_map_id == self.game_state.map.map_id
            ),
        )

    def on_npc_dialog_behavior_finished(self, error_code: str | None):
        if error_code is not None:
            raise UnhandledErrorCodeException(error_code)

        self.event_manager.on(
            StorageInventoryContentEvent,
            self.on_storage_inventory_content_event,
            originator=self,
            once=True,
        )

    def on_storage_inventory_content_event(self, msg: StorageInventoryContentEvent):
        self.event_manager.on(
            InventoryWeightEvent,
            callback=self.on_inventory_weight_event,
            originator=self,
            once=True,
            timeout=5,
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
