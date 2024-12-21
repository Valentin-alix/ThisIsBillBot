import datetime
from dataclasses import dataclass

from datas.protos.non_obf.game.exchange_pb2 import (
    ExchangeBidHouseItemAddedEvent,
    ExchangeBidHouseItemRemovedEvent,
    ExchangeBidHouseSearchRequest,
    ExchangeBidPriceEvent,
    ExchangeBidSellerStartedEvent,
    ObjectAveragePricesEvent,
)
from dofus_unity_reader.data_center.data_reader import DataReader
from dofus_unity_reader.enums.category_item_enum import CategoryEnum
from dofus_unity_reader.enums.type_item_enum import TypeItemEnum

from src.controller.sale_hotel import SaleHotelController
from src.core.config import get_time_beween_sale_hotel_prices
from src.core.engine.items.item import GATHERER_ITEM_GIDS
from src.core.engine.npcs.npc_info import NpcInfo
from src.core.frames.frame import Frame
from src.core.game_constants import NPCs

# Items vendables
SELLABLE_ITEMS = (
    GATHERER_ITEM_GIDS
    | DataReader().item_ids_by_type_id[TypeItemEnum.SUBSTRAT]
    | DataReader().item_ids_by_type_id[TypeItemEnum.ALLIAGE]
)
# Hôtels de vente par catégorie
SALE_HOTELS_BY_CATEGORY: dict[CategoryEnum, list[NpcInfo]] = {
    CategoryEnum.RESOURCES: [
        NPCs.BONTA_SALE_HOTEL_RES_SELL,
        NPCs.ASTRUB_SALE_HOTEL_RES_SELL,
    ],
    CategoryEnum.CONSUMABLES: [
        NPCs.BONTA_SALE_HOTEL_COM_SELL,
        NPCs.ASTRUB_SALE_HOTEL_COM_SELL,
    ],
}
UNSUB_SALE_HOTEL = [
    NPCs.ASTRUB_SALE_HOTEL_COM_SELL,
    NPCs.ASTRUB_SALE_HOTEL_RES_SELL,
]
SUB_SALE_HOTEL = [NPCs.BONTA_SALE_HOTEL_RES_SELL]


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
        self.game_state.sale_hotel.timedelta_for_next_sale_hotel_prices = (
            get_time_beween_sale_hotel_prices()
        )
        self.game_state.sale_hotel.last_time_updated_prices = datetime.datetime.now()
        self.game_state.sale_hotel.bid_seller_condition = msg.selling_conditions
        SaleHotelController().update_hdv(
            self.game_state.player.server_id,
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
            self.game_state.player.server_id,
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
            self.game_state.player.server_id,
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
            self.game_state.player.server_id,
            [
                (
                    object_average_price.average_price,
                    object_average_price.object_gid,
                )
                for object_average_price in msg.objects_average_prices
            ],
        )

    def on_exchange_bid_price_event(self, msg: ExchangeBidPriceEvent):
        SaleHotelController().add_multiple_avg_price_by_gid(
            self.game_state.player.server_id,
            [(msg.average_price, msg.object_gid)],
        )
