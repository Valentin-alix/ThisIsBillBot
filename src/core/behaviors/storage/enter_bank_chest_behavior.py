from dataclasses import dataclass

from protos.game.inventory_pb2 import StorageInventoryContentEvent
from src.core.behaviors.behavior import Behavior
from src.core.behaviors.movements.auto_trip.auto_trip_smart_behavior import (
    AutoTripSmartBehavior,
)
from src.core.behaviors.npc_dialog_behavior import NpcDialogBehavior
from src.core.behaviors.storage.consts import BANKS_NPC_INFOS
from src.exceptions import UnhandledErrorCodeException


@dataclass
class EnterBankChestBehavior(Behavior):
    npc_dialog_behavior: NpcDialogBehavior
    auto_trip_world_behavior: AutoTripSmartBehavior

    def run(self):
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
        self.finish()
