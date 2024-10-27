from dataclasses import dataclass

from d3_mapping.resources.protos.game.exchange_pb2 import (
    ExchangeBidHouseItemAddedEvent,
    ExchangeBidHouseItemRemovedEvent,
    ExchangeBidHouseSearchRequest,
    ExchangeBidPriceEvent,
    ExchangeBidSellerStartedEvent,
    ObjectAveragePricesEvent,
)

from src.controller.sale_hotel import SaleHotelController
from src.core.frames.frame import Frame


@dataclass
class SaleHotelFrame(Frame):
    def __post_init__(self):
        self.game_info_signals.disconnected.connect(
            self.game_state.sale_hotel.clear_state
        )
        self.event_manager.on(
            ExchangeBidSellerStartedEvent,
            self.on_exchange_bid_seller_started_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            ExchangeBidHouseItemAddedEvent,
            self.on_exchange_bid_house_item_added_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            ExchangeBidHouseItemRemovedEvent,
            self.on_exchange_bid_house_item_removed_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            ExchangeBidHouseSearchRequest,
            self.on_exchange_bid_house_search_request,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            ObjectAveragePricesEvent,
            self.on_object_average_prices_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            ExchangeBidPriceEvent,
            self.on_exchange_bid_price_event,
            originator=self,
            priority=self.priority,
        )

    def on_exchange_bid_seller_started_event(self, msg: ExchangeBidSellerStartedEvent):
        self.game_state.sale_hotel.bid_seller_condition = msg.selling_conditions
        SaleHotelController().update_hdv(
            self.game_state.player.character_id,
            {item.item.uid: (item.item.gid, item.item.quantity) for item in msg.items},
        )

    def on_exchange_bid_house_item_added_event(
        self, msg: ExchangeBidHouseItemAddedEvent
    ):
        SaleHotelController().add_gid_quantity_by_uid_by_player_id(
            self.game_state.player.character_id,
            msg.item.gid,
            msg.item.quantity,
            msg.item.uid,
        )

    def on_exchange_bid_house_item_removed_event(
        self, msg: ExchangeBidHouseItemRemovedEvent
    ):
        SaleHotelController().remove_uid_for_player_id(
            self.game_state.player.character_id,
            msg.sell_id,
        )

    def on_exchange_bid_house_search_request(self, msg: ExchangeBidHouseSearchRequest):
        if msg.follow:
            self.game_state.sale_hotel.current_search_item_gid = msg.object_gid
        else:
            self.game_state.sale_hotel.current_search_item_gid = None

    def on_object_average_prices_event(self, msg: ObjectAveragePricesEvent):
        SaleHotelController().add_multiple_avg_price_by_gid(
            [
                (
                    object_average_price.average_price,
                    object_average_price.object_gid,
                )
                for object_average_price in msg.objects_average_prices
            ]
        )

    def on_exchange_bid_price_event(self, msg: ExchangeBidPriceEvent):
        SaleHotelController().add_multiple_avg_price_by_gid(
            [(msg.average_price, msg.object_gid)]
        )
