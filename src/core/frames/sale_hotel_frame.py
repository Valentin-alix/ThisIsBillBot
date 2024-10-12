import datetime
from dataclasses import dataclass

from protos.game.exchange_pb2 import (
    ExchangeBidSellerStartedEvent,
    ExchangeBidHouseItemAddedEvent,
    ExchangeBidHouseItemRemovedEvent,
    ExchangeBidHouseSearchRequest,
)
from src.core.frames.frame import Frame
from src.core.states.sale_hotel_state import BID_SELLER_ITEM_BY_UID_BY_PLAYER_ID


@dataclass
class SaleHotelFrame(Frame):
    def __post_init__(self):
        self.event_manager.on(
            ExchangeBidSellerStartedEvent,
            self.on_exchange_bid_seller_started_event,
            originator=self,
        )
        self.event_manager.on(
            ExchangeBidHouseItemAddedEvent,
            self.on_exchange_bid_house_item_added_event,
            originator=self,
        )
        self.event_manager.on(
            ExchangeBidHouseItemRemovedEvent,
            self.on_exchange_bid_house_item_removed_event,
            originator=self,
        )
        self.event_manager.on(
            ExchangeBidHouseSearchRequest,
            self.on_exchange_bid_house_search_request,
            originator=self,
        )

    def on_exchange_bid_seller_started_event(self, msg: ExchangeBidSellerStartedEvent):
        self.game_state.sale_hotel.last_time_updated_prices = datetime.datetime.now()
        self.game_state.sale_hotel.bid_seller_condition = msg.selling_conditions
        BID_SELLER_ITEM_BY_UID_BY_PLAYER_ID[self.game_state.player.character_id] = {
            item.item.uid: item for item in msg.items
        }

    def on_exchange_bid_house_item_added_event(
        self, msg: ExchangeBidHouseItemAddedEvent
    ):
        BID_SELLER_ITEM_BY_UID_BY_PLAYER_ID[self.game_state.player.character_id][
            msg.item.uid
        ] = ExchangeBidSellerStartedEvent.ItemToSellInBid(
            item=msg.item, price=msg.price
        )

    def on_exchange_bid_house_item_removed_event(
        self, msg: ExchangeBidHouseItemRemovedEvent
    ):
        BID_SELLER_ITEM_BY_UID_BY_PLAYER_ID[self.game_state.player.character_id].pop(
            msg.sell_id, None
        )

    def on_exchange_bid_house_search_request(self, msg: ExchangeBidHouseSearchRequest):
        if msg.follow:
            self.game_state.sale_hotel.current_search_item_gid = msg.object_gid
        else:
            self.game_state.sale_hotel.current_search_item_gid = None
