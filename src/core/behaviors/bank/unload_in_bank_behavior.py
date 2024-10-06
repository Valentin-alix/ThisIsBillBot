from dataclasses import dataclass

from db_dofus_unity.protos.game.common_pb2 import DialogType
from db_dofus_unity.protos.game.dialog_pb2 import DialogLeaveRequest
from db_dofus_unity.protos.game.exchange_pb2 import (
    ExchangeObjectTransferAllFromInventoryRequest,
    ExchangeLeaveEvent,
)
from db_dofus_unity.protos.game.inventory_pb2 import (
    StorageInventoryContentEvent,
    InventoryWeightEvent,
)
from src.common.logger import Logger
from src.consts import BASE_RANGE
from src.core.behaviors.behavior import Behavior
from src.core.behaviors.movements.auto_trip_world_behavior import AutoTripWorldBehavior
from src.core.behaviors.npc_dialog_behavior import NpcDialogBehavior, NpcInfo

ASTRUB_BANK = NpcInfo(
    npc_action_id=3, npc_id=-20001, npc_map_id=192415750, reply_ids=[64361]
)


@dataclass
class UnloadInBankBehavior(Behavior):
    npc_dialog_behavior: NpcDialogBehavior
    auto_trip_world_behavior: AutoTripWorldBehavior

    def run(self):
        self.auto_trip_world_behavior.start(
            callback=lambda _: self.on_bank_map(),
            parent=self,
            dst={ASTRUB_BANK.npc_map_id},
        )

    def on_bank_map(self):
        self.event_manager.on(
            StorageInventoryContentEvent,
            self.on_storage_inventory_content_event,
            originator=self,
            once=True,
        )
        self.npc_dialog_behavior.start(
            callback=None,
            parent=self,
            npc_info=ASTRUB_BANK,
        )

    def on_storage_inventory_content_event(self, msg: StorageInventoryContentEvent):
        self.event_manager.on(
            InventoryWeightEvent,
            callback=self.on_inventory_weight_event,
            originator=self,
            once=True,
        )
        request = ExchangeObjectTransferAllFromInventoryRequest()
        self.run_timer(BASE_RANGE, lambda: self.event_manager.send(request))

    def on_inventory_weight_event(self, msg: InventoryWeightEvent):
        self.event_manager.on(
            ExchangeLeaveEvent,
            callback=self.on_exchange_leave_event,
            originator=self,
            once=True,
        )
        self.run_timer(BASE_RANGE, self.leave_all_dialogs)

    def on_exchange_leave_event(self, msg: ExchangeLeaveEvent):
        if msg.dialog_type != DialogType.DIALOG_EXCHANGE:
            Logger().error("dialog leaved was not dialog exchange ??")
        else:
            self.finish()

    def leave_all_dialogs(self):
        request = DialogLeaveRequest()
        self.event_manager.send(request)
        self.event_manager.send(request)
