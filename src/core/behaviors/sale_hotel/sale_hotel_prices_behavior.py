import datetime
import math
from dataclasses import dataclass, field
from enum import StrEnum, auto
from functools import partial
from typing import Iterable

from D3Database.data_center.data_reader import DataReader
from D3Database.data_center.i18n import I18N
from D3Database.enums.category_item_enum import CategoryEnum
from D3Mapping.d3_mapping.resources.protos.game.basic_pb2 import TextInformationEvent
from D3Mapping.d3_mapping.resources.protos.game.common_pb2 import ObjectItem
from D3Mapping.d3_mapping.resources.protos.game.dialog_pb2 import DialogLeaveRequest
from D3Mapping.d3_mapping.resources.protos.game.exchange_pb2 import (
    ExchangeBidHouseItemRemovedEvent,
    ExchangeBidHousePriceRequest,
    ExchangeBidHouseSearchRequest,
    ExchangeBidPriceEvent,
    ExchangeBidSellerStartedEvent,
    ExchangeLeaveEvent,
    ExchangeObjectModifyPricedRequest,
    ExchangeObjectMovePricedRequest,
)
from D3Mapping.d3_mapping.resources.protos.game.inventory_pb2 import (
    InventoryWeightEvent,
)
from src.controller.sale_hotel import SaleHotelController
from src.controller.scraping_d3_api.scraping_d3_client.scraping_d3_client.models.quantity_enum import (
    QuantityEnum,
)
from src.core.behaviors.behavior import Behavior
from src.core.behaviors.sale_hotel.enter_sale_hotel_sell_behavior import (
    EnterSaleHotelSellBehavior,
)
from src.core.behaviors.storage.loads.load_from_bank_behavior import (
    LoadFromBankBehavior,
)
from src.core.behaviors.storage.loads.load_from_guild_chest_behavior import (
    LoadFromGuildChestBehavior,
    LoadItemInfo,
)
from src.core.config import (
    BASE_RANGE,
    MIN_KAMAS_TO_GO_SALE_HOTEL,
    SMALL_RANGE,
    TINY_RANGE,
)
from src.core.engine.communications.text import TextEnum
from src.core.engine.economy.sale_hotel import (
    choose_quantity_to_sell,
    get_item_gids_to_sell,
    get_max_quantity_sell,
    get_price_for_sale_hotel,
    is_interesting_item_to_sell,
)
from src.core.game_constants import (
    TAB_BY_GID,
)
from src.core.states.guild_chest_state import CHEST_OBJECT_BY_GID_BY_TAB
from src.exceptions import UnexpectedStateException, UnhandledErrorCodeException


class SaleHotelErrorCode(StrEnum):
    NOT_ENOUGH_KAMAS = auto()


@dataclass
class SaleHotelPricesBehavior(Behavior):
    enter_sale_hotel_sell_behavior: EnterSaleHotelSellBehavior
    load_from_guild_chest_behavior: LoadFromGuildChestBehavior
    load_from_bank_behavior: LoadFromBankBehavior

    categories: set[CategoryEnum] = field(
        init=False, default_factory=lambda: set(CategoryEnum)
    )
    _curr_category: CategoryEnum = field(init=False, default=CategoryEnum.RESOURCES)

    def run(self) -> None:
        self.categories = {CategoryEnum.RESOURCES, CategoryEnum.CONSUMABLES}
        self.game_state.sale_hotel.last_time_updated_prices = datetime.datetime.now()

        if self.game_state.inventory.kamas < MIN_KAMAS_TO_GO_SALE_HOTEL:
            self.logger.warning(
                "Player does not have enough kamas, skipping sale hotel"
            )
            return self.finish()

        self.sell_next_category()

    def sell_next_category(self):
        if len(self.categories) == 0:
            return self.finish()

        self._curr_category = self.categories.pop()

        item_sell_quantity_by_gid = (
            SaleHotelController().get_item_sell_quantity_by_gid()
        )
        avg_price_by_gid = SaleHotelController().get_avg_price_by_gid()

        item_gids_to_sell = get_item_gids_to_sell(
            self.game_state.guild_chest.can_access_guild_chest,
            self.game_state.player.is_sub,
            self.game_state.inventory.bank_object_by_gid,
            item_sell_quantity_by_gid,
            self._curr_category,
            self.logger,
            avg_price_by_gid,
            CHEST_OBJECT_BY_GID_BY_TAB
            if self.game_state.guild_chest.can_access_guild_chest
            else None,
        )

        if len(item_gids_to_sell) == 0:
            return self.sell_next_category()

        self.logger.info(
            f"Item to sells : {[I18N().name_by_id[DataReader().item_by_id[gid].nameId or 0] for gid in item_gids_to_sell]}"
        )

        load_items_infos: list[LoadItemInfo] = []
        for item_gid in item_gids_to_sell:
            max_quantity_sell = get_max_quantity_sell(item_gid)
            load_item_info = LoadItemInfo(
                item_gid=item_gid,
                remaining_quantity=min(
                    max(
                        max_quantity_sell - item_sell_quantity_by_gid.get(item_gid, 0),
                        0,
                    ),
                    math.floor(max_quantity_sell / 4),
                ),
                tab=TAB_BY_GID.get(item_gid, 0),
            )
            load_items_infos.append(load_item_info)

        self.load_items(load_items_infos, item_gids_to_sell)

    def load_items(
        self, load_items_infos: list[LoadItemInfo], item_gids_to_sell: list[int]
    ):
        self.logger.info(f"Gonna load and sell : {load_items_infos}")
        if self.game_state.guild_chest.can_access_guild_chest:
            self.load_from_guild_chest_behavior.start(
                callback=partial(
                    self.on_loaded_behavior_finished, item_ids_to_sell=item_gids_to_sell
                ),
                parent=self,
                load_items_infos=load_items_infos,
            )
        else:
            self.load_from_bank_behavior.start(
                callback=partial(
                    self.on_loaded_behavior_finished, item_ids_to_sell=item_gids_to_sell
                ),
                parent=self,
                load_items_infos=load_items_infos,
            )

    def on_loaded_behavior_finished(
        self,
        error_code: str | None,
        load_items_infos: list[LoadItemInfo],
        item_ids_to_sell: list[int],
    ):
        if error_code is not None:
            return self.finish(error_code)

        self.enter_sale_hotel_sell_behavior.start(
            callback=partial(
                self.on_enter_sale_hotel_sell_behavior_finished,
                load_items_infos=load_items_infos,
                item_ids_to_sell=item_ids_to_sell,
            ),
            parent=self,
            category=self._curr_category,
        )

    def on_enter_sale_hotel_sell_behavior_finished(
        self,
        error_code: str | None,
        items: Iterable[ExchangeBidSellerStartedEvent.ItemToSellInBid],
        load_items_infos: list[LoadItemInfo],
        item_ids_to_sell: list[int],
    ):
        if error_code is not None:
            raise UnhandledErrorCodeException(error_code)
        self.sell_inventory(
            items=items,
            load_items_infos=load_items_infos,
            item_ids_to_sell=item_ids_to_sell,
        )

    def sell_inventory(
        self,
        items: Iterable[ExchangeBidSellerStartedEvent.ItemToSellInBid],
        load_items_infos: list[LoadItemInfo],
        item_ids_to_sell: list[int],
    ):
        item_to_sells_in_inventory = [
            object.item
            for object in self.game_state.inventory.objects_by_uid.values()
            if object.item.gid in item_ids_to_sell
        ]
        self.logger.info(
            f"Gonna sell in inventory : {[item.gid for item in item_to_sells_in_inventory]}"
        )
        self.create_all_prices(
            item_to_sells_in_inventory=item_to_sells_in_inventory,
            items=items,
            load_items_infos=load_items_infos,
            item_ids_to_sell=item_ids_to_sell,
        )

    def create_all_prices(
        self,
        item_to_sells_in_inventory: list[ObjectItem],
        item_ids_to_sell: list[int],
        items: Iterable[ExchangeBidSellerStartedEvent.ItemToSellInBid],
        load_items_infos: list[LoadItemInfo],
    ):
        while True:
            if len(item_to_sells_in_inventory) == 0:
                if len(load_items_infos) == 0:
                    self.logger.info("No more item to sell, lets update prices")
                    return self.update_all_prices(list(items))

                self.event_manager.on(
                    ExchangeLeaveEvent,
                    callback=lambda _: self.load_items(
                        load_items_infos, item_ids_to_sell
                    ),
                    originator=self,
                    once=True,
                )
                return self.leave_all_dialogs()

            next_item = item_to_sells_in_inventory.pop()
            if is_interesting_item_to_sell(
                next_item, SaleHotelController().get_avg_price_by_gid()
            ):
                break

        self.logger.info(
            f"Sell item {next_item.gid} with quantity {next_item.quantity}"
        )
        self.event_manager.on(
            ExchangeBidHouseSearchRequest,
            partial(
                self.on_exchange_bid_house_search_request_follow,
                item_to_sells_in_inventory=item_to_sells_in_inventory,
                item_ids_to_sell=item_ids_to_sell,
                items=items,
                load_items_infos=load_items_infos,
                next_item=next_item,
            ),
            originator=self,
        )
        self.run_timer(SMALL_RANGE, lambda: self.open_item(next_item.gid))

    def open_item(self, item_gid: int):
        if self.game_state.sale_hotel.current_search_item_gid is not None:
            req = ExchangeBidHouseSearchRequest(
                object_gid=self.game_state.sale_hotel.current_search_item_gid,
                follow=False,
            )
            self.event_manager.send(req)
        req = ExchangeBidHouseSearchRequest(object_gid=item_gid, follow=True)
        self.event_manager.send(req)

    def on_exchange_bid_house_search_request_follow(
        self,
        msg: ExchangeBidHouseSearchRequest,
        item_to_sells_in_inventory: list[ObjectItem],
        item_ids_to_sell: list[int],
        items: Iterable[ExchangeBidSellerStartedEvent.ItemToSellInBid],
        load_items_infos: list[LoadItemInfo],
        next_item: ObjectItem,
    ):
        if not msg.follow:
            return
        self.event_manager.clear_listener_by_origin_and_type(
            ExchangeBidHouseSearchRequest, self
        )
        self.event_manager.on(
            ExchangeBidPriceEvent,
            partial(
                self.on_exchange_bid_price_event_after_select_for_create_price,
                item_to_sells_in_inventory=item_to_sells_in_inventory,
                item=next_item,
                items=items,
                load_items_infos=load_items_infos,
                item_ids_to_sell=item_ids_to_sell,
            ),
            originator=self,
            once=True,
        )
        req = ExchangeBidHousePriceRequest(object_gid=msg.object_gid)
        self.event_manager.send(req)

    def on_exchange_bid_price_event_after_select_for_create_price(
        self,
        msg: ExchangeBidPriceEvent,
        item_to_sells_in_inventory: list[ObjectItem],
        item: ObjectItem,
        items: Iterable[ExchangeBidSellerStartedEvent.ItemToSellInBid],
        load_items_infos: list[LoadItemInfo],
        item_ids_to_sell: list[int],
    ):
        self.create_price(
            list(msg.bid_price_for_seller.minimal_prices),
            item,
            item_to_sells_in_inventory=item_to_sells_in_inventory,
            load_items_infos=load_items_infos,
            items=items,
            item_ids_to_sell=item_ids_to_sell,
        )

    def create_price(
        self,
        minimal_prices: list[int],
        item: ObjectItem,
        item_to_sells_in_inventory: list[ObjectItem],
        items: Iterable[ExchangeBidSellerStartedEvent.ItemToSellInBid],
        load_items_infos: list[LoadItemInfo],
        item_ids_to_sell: list[int],
    ):
        avg_price_by_gid = SaleHotelController().get_avg_price_by_gid()

        if not is_interesting_item_to_sell(item, avg_price_by_gid):
            return self.create_all_prices(
                load_items_infos=load_items_infos,
                items=items,
                item_to_sells_in_inventory=item_to_sells_in_inventory,
                item_ids_to_sell=item_ids_to_sell,
            )

        quantity_to_sell, quantity_index = choose_quantity_to_sell(
            item, avg_price_by_gid
        )

        minimal_price_in_sale_bots = (
            SaleHotelController()
            .get_minimal_price_by_gid_and_quantity()
            .get((item.gid, quantity_to_sell))
        )
        minimal_price_in_sale = get_price_for_sale_hotel(
            list(minimal_prices), quantity_to_sell
        )
        price_for_quantity = minimal_price_in_sale
        if minimal_price_in_sale_bots != minimal_price_in_sale:
            price_for_quantity -= 1

        self.logger.info(
            f"Price for {quantity_to_sell} for item {item.gid} : {price_for_quantity}"
        )
        if price_for_quantity <= 0:
            # it's useless to sell this, so skip
            return self.create_all_prices(
                load_items_infos=load_items_infos,
                items=items,
                item_to_sells_in_inventory=item_to_sells_in_inventory,
                item_ids_to_sell=item_ids_to_sell,
            )

        if self.game_state.sale_hotel.bid_seller_condition is None:
            raise UnexpectedStateException("we should have bid seller infos")

        count_item_in_sale = len(
            SaleHotelController()
            .get_hdv_by_uid_by_player()
            .get(self.game_state.player.character_id, {})
        )
        self.logger.info(
            f"item in sale : {count_item_in_sale}, max item possible in sale : {self.game_state.sale_hotel.bid_seller_condition.max_item_per_account}"
        )
        if self.game_state.sale_hotel.is_full_object_in_sale_hotel:
            self.logger.info("Sale hotel is full of object, let's update prices")
            return self.update_all_prices(list(items))

        if price_for_quantity * 0.02 > self.game_state.inventory.kamas:
            self.event_manager.on(
                ExchangeLeaveEvent,
                callback=lambda _: self.finish(SaleHotelErrorCode.NOT_ENOUGH_KAMAS),
                originator=self,
                once=True,
            )
            return self.leave_all_dialogs()

        self.event_manager.on(
            InventoryWeightEvent,
            lambda _: self.on_inventory_weight_event_after_created_price(
                item=item,
                minimal_prices=minimal_prices,
                item_to_sells_in_inventory=item_to_sells_in_inventory,
                load_items_infos=load_items_infos,
                items=items,
                item_ids_to_sell=item_ids_to_sell,
            ),
            originator=self,
            once=True,
        )
        self.event_manager.clear_listener_by_origin_and_type(TextInformationEvent, self)
        self.event_manager.on(
            TextInformationEvent,
            partial(self.on_text_information_event, items=items),
            originator=self,
        )
        self.logger.info(f"Remaining quantity of item {item.gid} : {item.quantity}")
        req = ExchangeObjectMovePricedRequest(
            object_uid=item.uid, quantity=quantity_to_sell, price=price_for_quantity
        )
        item.quantity -= quantity_to_sell  # bc these items instance are not linked to new items received in msg
        self.run_timer(TINY_RANGE, lambda: self.event_manager.send(req))

    def on_text_information_event(
        self,
        msg: TextInformationEvent,
        items: Iterable[ExchangeBidSellerStartedEvent.ItemToSellInBid],
    ):
        if msg.message_id != TextEnum.FULL_PLACE_SALE_HOTEL:
            return
        self.event_manager.clear_listener_by_origin_and_type(InventoryWeightEvent, self)
        self.event_manager.clear_listener_by_origin_and_type(TextInformationEvent, self)
        self.event_manager.clear_listener_by_origin_and_type(InventoryWeightEvent, self)
        self.logger.info(
            "Sale hotel is full, let's update prices (from text info event)"
        )
        self.update_all_prices(list(items))

    def on_inventory_weight_event_after_created_price(
        self,
        minimal_prices: list[int],
        item: ObjectItem,
        item_to_sells_in_inventory: list[ObjectItem],
        items: Iterable[ExchangeBidSellerStartedEvent.ItemToSellInBid],
        load_items_infos: list[LoadItemInfo],
        item_ids_to_sell: list[int],
    ):
        self.logger.info("Successfully created price, move on to next item quantity")
        self.create_price(
            minimal_prices=minimal_prices,
            item=item,
            item_to_sells_in_inventory=item_to_sells_in_inventory,
            items=items,
            load_items_infos=load_items_infos,
            item_ids_to_sell=item_ids_to_sell,
        )

    def update_all_prices(
        self, items: list[ExchangeBidSellerStartedEvent.ItemToSellInBid]
    ):
        if len(items) == 0:
            self.event_manager.on(
                ExchangeLeaveEvent,
                lambda _: self.sell_next_category(),
                originator=self,
                once=True,
            )
            return self.leave_all_dialogs()
        self.logger.info("Update prices of all item in sale hotel")
        item = items[0]
        self.update_item_price(item.item.gid, items)

    def update_item_price(
        self, item_gid: int, items: list[ExchangeBidSellerStartedEvent.ItemToSellInBid]
    ):
        self.event_manager.on(
            ExchangeBidPriceEvent,
            partial(
                self.on_exchange_bid_price_event,
                items=items,
            ),
            originator=self,
            once=True,
        )
        self.logger.info(f"Updating item {item_gid}")
        req = ExchangeBidHousePriceRequest(object_gid=item_gid)
        self.run_timer(SMALL_RANGE, lambda: self.event_manager.send(req))

    def on_exchange_bid_price_event(
        self,
        msg: ExchangeBidPriceEvent,
        items: list[ExchangeBidSellerStartedEvent.ItemToSellInBid],
    ):
        price_for_one = get_price_for_sale_hotel(
            list(msg.bid_price_for_seller.minimal_prices), QuantityEnum.VALUE_1
        )
        price_for_ten = get_price_for_sale_hotel(
            list(msg.bid_price_for_seller.minimal_prices), QuantityEnum.VALUE_10
        )
        price_for_hundred = get_price_for_sale_hotel(
            list(msg.bid_price_for_seller.minimal_prices), QuantityEnum.VALUE_100
        )
        price_for_thousand = get_price_for_sale_hotel(
            list(msg.bid_price_for_seller.minimal_prices), QuantityEnum.VALUE_1000
        )

        minimal_price_by_gid_and_quantity = (
            SaleHotelController().get_minimal_price_by_gid_and_quantity()
        )
        if price_for_one != minimal_price_by_gid_and_quantity.get((msg.object_gid, 1)):
            price_for_one -= 1
        if price_for_ten != minimal_price_by_gid_and_quantity.get((msg.object_gid, 10)):
            price_for_ten -= 1
        if price_for_hundred != minimal_price_by_gid_and_quantity.get(
            (msg.object_gid, 100)
        ):
            price_for_hundred -= 1
        if price_for_thousand != minimal_price_by_gid_and_quantity.get(
            (msg.object_gid, 1000)
        ):
            price_for_thousand -= 1

        related_items = [item for item in items if item.item.gid == msg.object_gid]
        price_cost: float = 0
        requests_modify_price: list[ExchangeObjectModifyPricedRequest] = []

        for item in related_items:
            items.remove(item)
            if item.item.quantity == 1 and item.price != price_for_one:
                price = price_for_one
            elif item.item.quantity == 10 and item.price != price_for_ten:
                price = price_for_ten
            elif item.item.quantity == 100 and item.price != price_for_hundred:
                price = price_for_hundred
            elif item.item.quantity == 1000 and item.price != price_for_thousand:
                price = price_for_thousand
            else:
                continue
            if price <= 0:
                continue
            if (
                item.item.uid
                not in SaleHotelController()
                .get_hdv_by_uid_by_player()
                .get(self.game_state.player.character_id, {})
            ):
                self.logger.info(
                    f"item {item.item.uid} not in bid seller anymore, skip"
                )
                continue
            price_cost += price * 0.02
            if price_cost > self.game_state.inventory.kamas:
                break
            requests_modify_price.append(
                ExchangeObjectModifyPricedRequest(
                    object_uid=item.item.uid, quantity=item.item.quantity, price=price
                )
            )

        if len(requests_modify_price) == 0:
            self.logger.info("No request modify, go next item")
            self.update_all_prices(items)
        else:
            self.event_manager.on(
                ExchangeBidHouseItemRemovedEvent,
                partial(
                    self.on_exchange_bid_house_item_removed_event_after_updated,
                    items=items,
                    target_uid=requests_modify_price[-1].object_uid,
                ),
                originator=self,
            )

            def send_all_modify_price_req():
                for request_modify_price in requests_modify_price:
                    self.event_manager.send(request_modify_price)

            self.run_timer(BASE_RANGE, send_all_modify_price_req)

    def on_exchange_bid_house_item_removed_event_after_updated(
        self,
        msg: ExchangeBidHouseItemRemovedEvent,
        target_uid: int,
        items: list[ExchangeBidSellerStartedEvent.ItemToSellInBid],
    ):
        if msg.sell_id != target_uid:
            return
        self.event_manager.clear_listener_by_origin_and_type(
            ExchangeBidHouseItemRemovedEvent, originator=self
        )
        self.logger.info("Update all prices after item removed")
        self.run_timer(BASE_RANGE, lambda: self.update_all_prices(items))

    def leave_all_dialogs(self):
        request = DialogLeaveRequest()
        self.event_manager.send(request)
