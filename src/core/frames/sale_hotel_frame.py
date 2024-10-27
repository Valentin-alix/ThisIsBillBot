from dataclasses import dataclass
from threading import Thread
from typing import Iterable

from d3_mapping.resources.protos.game.exchange_pb2 import (
    ExchangeBidHouseItemAddedEvent,
    ExchangeBidHouseItemRemovedEvent,
    ExchangeBidHouseSearchRequest,
    ExchangeBidPriceEvent,
    ExchangeBidSellerStartedEvent,
    ExchangeTypesItemsExchangerDescriptionForUserEvent,
    ObjectAveragePricesEvent,
)

from scraping_d3_client.scraping_d3_client.api.default import (
    bulk_insert_item_price_history_item_price_history_bulk_insert_post,
)
from scraping_d3_client.scraping_d3_client.client import Client
from scraping_d3_client.scraping_d3_client.models.create_item_price_history_schema import (
    CreateItemPriceHistorySchema,
)
from scraping_d3_client.scraping_d3_client.models.quantity_enum import QuantityEnum
from src.const import BACKEND_URL
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
        self.event_manager.on(
            ExchangeTypesItemsExchangerDescriptionForUserEvent,
            callback=self.on_exchange_types_item_exchanger_description_for_user_event,
            originator=self,
            priority=self.priority,
        )

    def on_exchange_bid_seller_started_event(self, msg: ExchangeBidSellerStartedEvent):
        self.game_state.sale_hotel.bid_seller_condition = msg.selling_conditions
        SaleHotelController().update_hdv(
            self.game_state.player.character_id,
            {
                item.item.uid: (item.item.gid, item.item.quantity, item.price)
                for item in msg.items
            },
        )

    def on_exchange_bid_house_item_added_event(
        self, msg: ExchangeBidHouseItemAddedEvent
    ):
        SaleHotelController().add_gid_quantity_by_uid_by_player_id(
            self.game_state.player.character_id,
            msg.item.gid,
            msg.item.quantity,
            msg.price,
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
        self.register_prices(msg.bid_price_for_seller.minimal_prices, msg.object_gid)

    def on_exchange_types_item_exchanger_description_for_user_event(
        self, msg: ExchangeTypesItemsExchangerDescriptionForUserEvent
    ):
        if len(msg.item_descriptions) == 0:
            return
        item_description = msg.item_descriptions[0]
        self.register_prices(item_description.prices, item_description.gid)

    def register_prices(self, prices: Iterable[int], gid: int):
        item_prices_histories: list[CreateItemPriceHistorySchema] = []
        quantity_by_index: dict[int, QuantityEnum] = {
            0: QuantityEnum.VALUE_1,
            1: QuantityEnum.VALUE_10,
            2: QuantityEnum.VALUE_100,
            3: QuantityEnum.VALUE_1000,
        }
        for index, item_price in enumerate(prices):
            item_prices_histories.append(
                CreateItemPriceHistorySchema(
                    gid=gid,
                    quantity=quantity_by_index[index],
                    price=item_price if item_price > 0 else None,
                    server_id=self.game_state.player.server_id,
                )
            )

        def _silent_bulk_insert():
            try:
                with Client(base_url=BACKEND_URL) as client:
                    bulk_insert_item_price_history_item_price_history_bulk_insert_post.sync(
                        client=client, body=item_prices_histories
                    )
            except Exception as err:
                self.logger.warning(f"bulk_insert_prices failed: {err}")

        Thread(target=_silent_bulk_insert, daemon=True).start()
