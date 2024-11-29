from dataclasses import dataclass

from dofus_unity_reader.enums.category_item_enum import CategoryEnum
from datas.protos.non_obf.game.exchange_pb2 import (
    ExchangeBidSellerStartedEvent,
)
from datas.protos.non_obf.game.npc_pb2 import (
    NpcGenericActionRequest,
)

from src.core.behaviors.behavior import Behavior
from src.core.behaviors.sale_hotel.enter_sale_hotel_behavior import (
    EnterSaleHotelBehavior,
)
from src.core.config import BASE_RANGE
from src.core.engine.npcs.npc_info import NpcInfo


@dataclass
class EnterSaleHotelSellBehavior(Behavior):
    enter_sale_hotel_behavior: EnterSaleHotelBehavior

    def run(self, category: CategoryEnum) -> None:
        self.enter_sale_hotel_behavior.start(
            callback=self.on_entered_sale_hotel_behavior_finished,
            parent=self,
            category=category,
        )

    def on_entered_sale_hotel_behavior_finished(
        self, error_code: str | None, npc_info: NpcInfo
    ):
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
        self.send_message_delayed(req, BASE_RANGE)

    def on_exchange_bid_seller_started_event(self, msg: ExchangeBidSellerStartedEvent):
        self.finish(items=msg.items)
