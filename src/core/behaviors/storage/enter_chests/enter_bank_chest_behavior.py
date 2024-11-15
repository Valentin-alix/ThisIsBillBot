from dataclasses import dataclass
from enum import StrEnum, auto
from typing import Iterable

from d3_mapping.protocol.protocol_game import is_usable_msg
from d3_mapping.resources.protos.game.exchange_pb2 import ExchangeMoveKamaRequest
from d3_mapping.resources.protos.game.inventory_pb2 import (
    StorageInventoryContentEvent,
)

from src.core.behaviors.behavior import Behavior
from src.core.behaviors.movements.auto_trip.auto_trip_smart_behavior import (
    AutoTripSmartBehavior,
)
from src.core.behaviors.npcs.npc_dialog_behavior import (
    NpcDialogBehavior,
    NpcDialogErrorCode,
)
from src.core.config.storage import (
    BANKS_NPC_INFOS,
)
from src.core.config.timings import BASE_RANGE
from src.core.logic.map.map_tools import MapTools
from src.exceptions import UnhandledErrorCodeException


class EnterBankChestErrorCode(StrEnum):
    NOT_ENOUGH_KAMAS = auto()
    NOT_ENOUGH_LVL = auto()


@dataclass
class EnterBankChestBehavior(Behavior):
    npc_dialog_behavior: NpcDialogBehavior
    auto_trip_world_behavior: AutoTripSmartBehavior

    def run(self):
        if self.game_state.player.level < 10:
            return self.finish(EnterBankChestErrorCode.NOT_ENOUGH_LVL)

        bank_npc_infos = [
            npc_info
            for npc_info in BANKS_NPC_INFOS
            if self.game_state.player.is_sub
            or MapTools.is_map_allowed_for_unsub(npc_info.npc_map_id)
        ]

        self.auto_trip_world_behavior.start(
            callback=self.on_bank_map,
            parent=self,
            map_ids={bank.npc_map_id for bank in bank_npc_infos},
        )

    def on_bank_map(self, error_code: str | None):
        def forbidden_condition_dialog_params(dialog_params: Iterable[str]):
            return int(next(iter(dialog_params))) > self.game_state.inventory.kamas

        if error_code is not None:
            return self.finish(error_code)

        self.event_manager.on(
            StorageInventoryContentEvent,
            self.on_storage_inventory_content_event,
            originator=self,
            once=True,
        )

        self.npc_dialog_behavior.start(
            callback=self.on_npc_dialog_behavior_finished,
            parent=self,
            npc_dialog_info=next(
                bank
                for bank in BANKS_NPC_INFOS
                if bank.npc_map_id == self.game_state.map.map_id
            ),
            forbidden_condition_dialog_param=forbidden_condition_dialog_params,
        )

    def on_npc_dialog_behavior_finished(self, error_code: str | None):
        if error_code is NpcDialogErrorCode.FORBIDDEN_CONDITION:
            return self.finish(EnterBankChestErrorCode.NOT_ENOUGH_KAMAS)
        elif error_code is not None:
            raise UnhandledErrorCodeException(error_code)

    def on_storage_inventory_content_event(self, msg: StorageInventoryContentEvent):
        if not is_usable_msg(ExchangeMoveKamaRequest.DESCRIPTOR.full_name):
            return self.finish()

        if msg.kamas > 0:

            def move_kama():
                req = ExchangeMoveKamaRequest(quantity=-msg.kamas)
                self.event_manager.send(req)
                self.finish()

            self.run_timer(BASE_RANGE, move_kama)
        else:
            self.finish()
