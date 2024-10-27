import random
from dataclasses import dataclass
from functools import partial

from d3_mapping.resources.protos.game.dialog_pb2 import DialogLeaveRequest
from d3_mapping.resources.protos.game.exchange_pb2 import (
    ExchangeBidBuyerStartedEvent,
    ExchangeBidHouseSearchRequest,
    ExchangeBidHouseTypeRequest,
    ExchangeLeaveEvent,
    ExchangeTypesExchangerDescriptionForUserEvent,
    ExchangeTypesItemsExchangerDescriptionForUserEvent,
)

from src.core.behaviors.behavior import Behavior
from src.core.behaviors.sale_hotel.enter_sale_hotel_behavior import (
    EnterSaleHotelBehavior,
)
from src.core.config.timings import BASE_RANGE, BIG_RANGE
from src.interfaces.models.npc_info import NpcInfo

INTERVAL_BETWEEN_SCRAPING = 60 * 14


@dataclass
class SaleHotelScrapingBehavior(Behavior):
    """this behavior scraping the prices of the sale hotel regularly to update api"""

    enter_sale_hotel_behavior: EnterSaleHotelBehavior

    def run(self) -> None:
        self.go_to_sale_hotel()

    def go_to_sale_hotel(self):
        self.enter_sale_hotel_behavior.start(
            callback=self.on_entered_sale_hotel_behavior_finished, parent=self
        )

    def on_entered_sale_hotel_behavior_finished(
        self,
        error_code: str | None,
        npc_info: NpcInfo,
        bid_buyer_msg: ExchangeBidBuyerStartedEvent,
    ):
        self.run_timer(
            BIG_RANGE,
            lambda: self.search_items_types_prices(
                None, None, list(bid_buyer_msg.selling_conditions.types)
            ),
        )

    def search_items_types_prices(
        self,
        previous_type_item_id: int | None,
        previous_gid: int | None,
        types_items_ids: list[int],
    ):
        if len(types_items_ids) == 0:
            return self.finish()

        type_item_id_to_check = types_items_ids.pop()
        self.event_manager.on(
            ExchangeTypesExchangerDescriptionForUserEvent,
            callback=partial(
                self.on_exchange_type_exchanger_description_for_user_event,
                types_items_ids=types_items_ids,
                current_type_item_id=type_item_id_to_check,
                previous_gid=previous_gid,
            ),
            originator=self,
            once=True,
        )

        if previous_type_item_id is not None:
            self.event_manager.send(
                ExchangeBidHouseTypeRequest(type_id=previous_type_item_id, follow=False)
            )
        req = ExchangeBidHouseTypeRequest(type_id=type_item_id_to_check, follow=True)
        self.event_manager.send(req)

    def on_exchange_type_exchanger_description_for_user_event(
        self,
        msg: ExchangeTypesExchangerDescriptionForUserEvent,
        types_items_ids: list[int],
        current_type_item_id: int,
        previous_gid: int | None,
    ):
        self.run_timer(
            BASE_RANGE,
            lambda: self.search_items_prices(
                list(msg.type_description),
                types_items_ids,
                previous_gid,
                current_type_item_id,
            ),
        )

    def search_items_prices(
        self,
        items_gid: list[int],
        types_items_ids: list[int],
        previous_gid: int | None,
        current_type_item_id: int,
    ):
        if len(items_gid) == 0:
            return self.run_timer(
                BIG_RANGE,
                lambda: self.search_items_types_prices(
                    current_type_item_id, previous_gid, types_items_ids
                ),
            )
        gid = items_gid.pop()
        self.event_manager.on(
            ExchangeTypesItemsExchangerDescriptionForUserEvent,
            callback=lambda _: self.run_timer(
                BASE_RANGE,
                lambda: self.search_items_prices(
                    items_gid,
                    types_items_ids,
                    previous_gid=gid,
                    current_type_item_id=current_type_item_id,
                ),
            ),
            originator=self,
            once=True,
        )

        if previous_gid is not None:
            self.event_manager.send(
                ExchangeBidHouseSearchRequest(object_gid=previous_gid, follow=False)
            )
        req = ExchangeBidHouseSearchRequest(object_gid=gid, follow=True)
        self.event_manager.send(req)

    def leave_sale_hotel(self):
        self.event_manager.on(
            ExchangeLeaveEvent,
            callback=lambda _: self.run_timer(
                INTERVAL_BETWEEN_SCRAPING * random.uniform(0.75, 1.25),
                self.go_to_sale_hotel,
            ),
            originator=self,
            once=True,
        )
        self.event_manager.send(DialogLeaveRequest())
