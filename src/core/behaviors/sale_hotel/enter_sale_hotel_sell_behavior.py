from dataclasses import dataclass

from datas.protos.non_obf.game.exchange_pb2 import (
    ExchangeBidSellerStartedEvent,
)
from datas.protos.non_obf.game.npc_pb2 import (
    NpcGenericActionRequest,
)
from dofus_unity_reader.game_constants.item import CategoryItemEnum
from dofus_unity_reader.game_constants.npc import NpcInfo

from src.core.behaviors.behavior import Behavior
from src.core.behaviors.sale_hotel.enter_sale_hotel_behavior import (
    EnterSaleHotelBehavior,
)
from src.core.frames.sale_hotel_frame import SALE_HOTELS_BY_CATEGORY
from src.core.states.dialog_state import OpenDialogKind
from src.services.human_timings import HumanTimingsService


@dataclass
class EnterSaleHotelSellBehavior(Behavior):
    enter_sale_hotel_behavior: EnterSaleHotelBehavior

    def run(self, category: CategoryItemEnum) -> None:
        if self._is_already_on_the_right_sale_hotel(category):
            self.logger.info("Sale hotel already open on this category, reusing it")
            return self.finish(items=self.game_state.sale_hotel.items_in_sale)

        self.enter_sale_hotel_behavior.start(
            callback=self.on_entered_sale_hotel_behavior_finished,
            parent=self,
            category=category,
        )

    def _is_already_on_the_right_sale_hotel(self, category: CategoryItemEnum) -> bool:
        if not self.game_state.dialog.is_open(OpenDialogKind.BID_HOUSE_SELL):
            return False
        return self.game_state.map.map_id in {
            npc_info.npc_map_id for npc_info in SALE_HOTELS_BY_CATEGORY[category]
        }

    def on_entered_sale_hotel_behavior_finished(self, error_code: str | None, npc_info: NpcInfo):
        self.raise_if_error(error_code)
        self.event_manager.on(
            ExchangeBidSellerStartedEvent,
            self.on_exchange_bid_seller_started_event,
            originator=self,
            once=True,
        )
        npc_id = self.game_state.entity.resolve_npc_id(npc_info)
        req = NpcGenericActionRequest(
            npc_id=npc_id,
            npc_map_id=npc_info.npc_map_id,
            npc_action_id=npc_info.npc_action_id,
        )
        self.send_message_delayed(req, HumanTimingsService().get_timing_base_action())

    def on_exchange_bid_seller_started_event(self, msg: ExchangeBidSellerStartedEvent):
        self.finish(items=msg.items)
