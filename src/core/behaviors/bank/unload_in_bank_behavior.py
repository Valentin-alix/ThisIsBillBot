from dataclasses import dataclass

from db_dofus_unity.protos.game.dialog_pb2 import DialogLeaveRequest, DialogLeaveEvent
from db_dofus_unity.protos.game.exchange_pb2 import (
    ExchangeObjectTransferAllFromInventoryRequest,
    ExchangeLeaveEvent,
)
from db_dofus_unity.protos.game.inventory_pb2 import (
    StorageInventoryContentEvent,
    InventoryWeightEvent,
)
from src.core.behaviors.behavior import Behavior
from src.core.behaviors.npc_dialog_behavior import NpcDialogBehavior

ASTRUB_BANK = {
    "npcActionId": 3,
    "npcId": -20001,
    "npcMapId": 192415750,
    "openBankReplyId": 64361,
}


@dataclass
class UnloadInBankBehavior(Behavior):
    npc_dialog_behavior: NpcDialogBehavior

    def run(self):
        self.event_manager.on(
            StorageInventoryContentEvent,
            self.on_storage_inventory_content_event,
            originator=self,
            once=True,
        )
        self.npc_dialog_behavior.start(
            callback=None,
            parent=self,
            npc_id=ASTRUB_BANK["npcId"],
            npc_action_id=ASTRUB_BANK["npcActionId"],
            npc_map_id=ASTRUB_BANK["npcMapId"],
            reply_ids=[ASTRUB_BANK["openBankReplyId"]],
        )

    def on_storage_inventory_content_event(self, msg: StorageInventoryContentEvent):
        self.event_manager.on(
            InventoryWeightEvent,
            callback=self.on_inventory_weight_event,
            originator=self,
            once=True,
        )
        request = ExchangeObjectTransferAllFromInventoryRequest()
        self.event_manager.send(request)

    def on_inventory_weight_event(self, msg: InventoryWeightEvent):
        self.event_manager.on(
            ExchangeLeaveEvent,
            callback=lambda _: self.finish(),
            originator=self,
            once=True,
        )
        self.quit_dialogs()

    def quit_dialogs(self):
        self.event_manager.on(
            DialogLeaveEvent,
            callback=lambda _: self.finish(),
            originator=self,
            once=True,
        )
        request = DialogLeaveRequest()
        self.event_manager.send(request)
        self.event_manager.send(request)
