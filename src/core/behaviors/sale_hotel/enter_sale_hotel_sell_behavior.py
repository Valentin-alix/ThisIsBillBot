from dataclasses import dataclass

from d3_mapping.resources.protos.game.exchange_pb2 import (
    ExchangeBidSellerStartedEvent,
)
from d3_mapping.resources.protos.game.npc_pb2 import NpcGenericActionRequest
from enums.category_item_enum import CategoryEnum

from src.core.behaviors.behavior import Behavior
from src.core.behaviors.sale_hotel.enter_sale_hotel_behavior import (
    EnterSaleHotelBehavior,
)
from src.core.config.timings import BASE_RANGE
from src.exceptions import UnhandledErrorCodeException
from src.interfaces.models.npc_info import NpcInfo


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
        if error_code is not None:
            raise UnhandledErrorCodeException(error_code)
        self.event_manager.on(
            ExchangeBidSellerStartedEvent,
            self.on_exchange_bid_seller_started_event,
            originator=self,
            once=True,
        )
        req = NpcGenericActionRequest(
            npc_id=npc_info.npc_id,
            npc_map_id=npc_info.npc_map_id,
            npc_action_id=npc_info.npc_action_id,
        )
        self.run_timer(BASE_RANGE, lambda: self.event_manager.send(req))

    def on_exchange_bid_seller_started_event(self, msg: ExchangeBidSellerStartedEvent):
        self.finish(items=msg.items)
