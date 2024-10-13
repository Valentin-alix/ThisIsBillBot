import datetime
import random
from collections import defaultdict
from dataclasses import dataclass
from functools import partial
from typing import Iterable

from protos.game.common_pb2 import ObjectItem
from protos.game.dialog_pb2 import DialogLeaveRequest
from protos.game.exchange_pb2 import (
    ExchangeBidSellerStartedEvent,
    ExchangeBidHousePriceRequest,
    ExchangeObjectModifyPricedRequest,
    ExchangeBidPriceEvent,
    ExchangeBidHouseItemRemovedEvent,
    ExchangeLeaveEvent,
    ExchangeBidHouseSearchRequest,
    ExchangeObjectMovePricedRequest,
)
from protos.game.inventory_pb2 import InventoryWeightEvent
from src.const import VERY_SMALL_RANGE
from src.core.behaviors.behavior import Behavior
from src.core.behaviors.sale_hotel.enter_sale_hotel_sell_behavior import (
    EnterSaleHotelSellBehavior,
)
from src.core.behaviors.storage.consts import (
    GATHERER_ITEM_IDS,
    USEFUL_INGREDIENT_IDS,
    GATHERER_ITEM_TABS,
)
from src.core.behaviors.storage.load_from_guild_chest_behavior import (
    LoadFromGuildChestBehavior,
    LoadItemInfo,
)
from src.core.logic.prices.price import get_price_for_sale_hotel, QuantityIndex
from src.core.states.guild_chest_state import CHEST_OBJECT_BY_GID_BY_TAB
from src.core.states.sale_hotel_state import (
    BID_SELLER_ITEM_BY_UID_BY_PLAYER_ID,
    AVERAGE_PRICE_BY_GID,
)
from src.exceptions import UnhandledErrorCodeException, UnexpectedStateException


@dataclass
class SaleHotelPricesBehavior(Behavior):
    enter_sale_hotel_sell_behavior: EnterSaleHotelSellBehavior
    load_from_guild_chest_behavior: LoadFromGuildChestBehavior

    def run(self) -> None:
        self.game_state.sale_hotel.last_time_updated_prices = datetime.datetime.now()

        gatherer_object_tab = CHEST_OBJECT_BY_GID_BY_TAB.get(GATHERER_ITEM_TABS)
        item_ids_to_sell = [
            item_id
            for item_id in GATHERER_ITEM_IDS
            if item_id not in USEFUL_INGREDIENT_IDS
        ]
        if gatherer_object_tab is not None:
            item_ids_to_sell.sort(
                key=lambda item_id: (
                    random.random()
                    * related_object.item.quantity
                    * AVERAGE_PRICE_BY_GID.get(related_object.item.gid, 1000)
                    if (related_object := gatherer_object_tab.get(item_id))
                    else 0
                ),
                reverse=True,
            )
        else:
            item_ids_to_sell.sort(
                key=lambda item_id: (
                    random.random() * AVERAGE_PRICE_BY_GID.get(item_id, 1000)
                ),
                reverse=True,
            )

        # get sum quantity of item already in sale hotel by gid
        item_sell_quantity_by_gid: dict[int, int] = defaultdict(int)
        for bid_seller_item in BID_SELLER_ITEM_BY_UID_BY_PLAYER_ID.values():
            for seller_item in bid_seller_item.values():
                item_sell_quantity_by_gid[
                    seller_item.item.gid
                ] += seller_item.item.quantity

        load_items_infos: list[LoadItemInfo] = []
        for item_gid in item_ids_to_sell:
            load_item_info = LoadItemInfo(
                item_gid=item_gid,
                remaining_quantity=max(
                    5000 - item_sell_quantity_by_gid.get(item_gid, 0), 0
                ),
            )
            load_items_infos.append(load_item_info)

        self.logger.info(f"Gonna load and sell : {load_items_infos}")

        self.load_from_guild_chest_behavior.start(
            callback=partial(
                self.on_load_from_guild_chest_behavior_finished,
                item_ids_to_sell=item_ids_to_sell,
            ),
            parent=self,
            load_items_infos=load_items_infos,
        )

    def on_load_from_guild_chest_behavior_finished(
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
        self.choose_and_create_item_price(
            item_to_sells_in_inventory=item_to_sells_in_inventory,
            items=items,
            load_items_infos=load_items_infos,
            item_ids_to_sell=item_ids_to_sell,
        )

    def choose_and_create_item_price(
        self,
        item_to_sells_in_inventory: list[ObjectItem],
        item_ids_to_sell: list[int],
        items: Iterable[ExchangeBidSellerStartedEvent.ItemToSellInBid],
        load_items_infos: list[LoadItemInfo],
    ):
        while True:
            if len(item_to_sells_in_inventory) == 0:
                if len(load_items_infos) == 0:
                    return self.choose_and_update_item_price(list(items))
                self.event_manager.on(
                    ExchangeLeaveEvent,
                    lambda _: self.load_from_guild_chest_behavior.start(
                        callback=partial(
                            self.on_load_from_guild_chest_behavior_finished,
                            item_ids_to_sell=item_ids_to_sell,
                        ),
                        parent=self,
                        load_items_infos=load_items_infos,
                    ),
                    originator=self,
                    once=True,
                )
                return self.leave_all_dialogs()

            next_item = item_to_sells_in_inventory.pop()
            if next_item.quantity >= 100:
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
        self.run_timer(VERY_SMALL_RANGE, lambda: self.open_item(next_item.gid))

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
        self.run_timer((0.001, 0.01), lambda: self.event_manager.send(req))

    def on_exchange_bid_price_event_after_select_for_create_price(
        self,
        msg: ExchangeBidPriceEvent,
        item_to_sells_in_inventory: list[ObjectItem],
        item: ObjectItem,
        items: Iterable[ExchangeBidSellerStartedEvent.ItemToSellInBid],
        load_items_infos: list[LoadItemInfo],
        item_ids_to_sell: list[int],
    ):
        price_for_hundred_quantity = (
            get_price_for_sale_hotel(
                list(msg.bid_price_for_seller.minimal_prices), QuantityIndex.HUNDRED
            )
            - 1
        )
        self.logger.info(
            f"Price for hundred for item {item.gid} : {price_for_hundred_quantity}"
        )
        if price_for_hundred_quantity <= 0:
            return self.choose_and_create_item_price(
                load_items_infos=load_items_infos,
                items=items,
                item_to_sells_in_inventory=item_to_sells_in_inventory,
                item_ids_to_sell=item_ids_to_sell,
            )
        self.sell_item(
            item,
            quantity=100,
            price=price_for_hundred_quantity,
            item_to_sells_in_inventory=item_to_sells_in_inventory,
            load_items_infos=load_items_infos,
            items=items,
            item_ids_to_sell=item_ids_to_sell,
        )

    def sell_item(
        self,
        item: ObjectItem,
        quantity: int,
        price: int,
        item_to_sells_in_inventory: list[ObjectItem],
        items: Iterable[ExchangeBidSellerStartedEvent.ItemToSellInBid],
        load_items_infos: list[LoadItemInfo],
        item_ids_to_sell: list[int],
    ):
        if self.game_state.sale_hotel.bid_seller_condition is None:
            raise UnexpectedStateException("we should have bid seller infos")
        count_item_in_sale = len(
            BID_SELLER_ITEM_BY_UID_BY_PLAYER_ID[self.game_state.player.character_id]
        )
        self.logger.info(
            f"item in sale : {count_item_in_sale}, max item possible in sale : {self.game_state.sale_hotel.bid_seller_condition.max_item_per_account}"
        )
        if (
            count_item_in_sale
            == self.game_state.sale_hotel.bid_seller_condition.max_item_per_account
        ):
            self.logger.info("Sale hotel is full of object, let's update prices")
            return self.choose_and_update_item_price(list(items))
        if item.quantity < quantity:
            self.logger.info(
                f"{item.gid} doesn't have enough quantity : {item.quantity}, go to next item"
            )
            return self.choose_and_create_item_price(
                load_items_infos=load_items_infos,
                items=items,
                item_to_sells_in_inventory=item_to_sells_in_inventory,
                item_ids_to_sell=item_ids_to_sell,
            )
        self.event_manager.on(
            InventoryWeightEvent,
            lambda _: self.on_inventory_weight_event_after_created_price(
                item=item,
                quantity=quantity,
                price=price,
                item_to_sells_in_inventory=item_to_sells_in_inventory,
                load_items_infos=load_items_infos,
                items=items,
                item_ids_to_sell=item_ids_to_sell,
            ),
            originator=self,
            once=True,
        )
        item.quantity -= quantity
        self.logger.info(f"Remaining quantity of item {item.gid} : {item.quantity}")
        req = ExchangeObjectMovePricedRequest(
            object_uid=item.uid, quantity=quantity, price=price
        )
        self.run_timer(VERY_SMALL_RANGE, lambda: self.event_manager.send(req))

    def on_inventory_weight_event_after_created_price(
        self,
        item: ObjectItem,
        quantity: int,
        price: int,
        item_to_sells_in_inventory: list[ObjectItem],
        items: Iterable[ExchangeBidSellerStartedEvent.ItemToSellInBid],
        load_items_infos: list[LoadItemInfo],
        item_ids_to_sell: list[int],
    ):

        self.logger.info("Successfully created price, move on to next item quantity")
        self.sell_item(
            item=item,
            quantity=quantity,
            price=price,
            item_to_sells_in_inventory=item_to_sells_in_inventory,
            items=items,
            load_items_infos=load_items_infos,
            item_ids_to_sell=item_ids_to_sell,
        )

    def choose_and_update_item_price(
        self, items: list[ExchangeBidSellerStartedEvent.ItemToSellInBid]
    ):
        if len(items) == 0:
            self.event_manager.on(
                ExchangeLeaveEvent, lambda _: self.finish(), originator=self, once=True
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
        req = ExchangeBidHousePriceRequest(object_gid=item_gid)
        self.run_timer(VERY_SMALL_RANGE, lambda: self.event_manager.send(req))

    def on_exchange_bid_price_event(
        self,
        msg: ExchangeBidPriceEvent,
        items: list[ExchangeBidSellerStartedEvent.ItemToSellInBid],
    ):
        price_for_one = get_price_for_sale_hotel(
            list(msg.bid_price_for_seller.minimal_prices), QuantityIndex.ONE
        )
        price_for_ten = get_price_for_sale_hotel(
            list(msg.bid_price_for_seller.minimal_prices), QuantityIndex.TEN
        )
        price_for_hundred = get_price_for_sale_hotel(
            list(msg.bid_price_for_seller.minimal_prices), QuantityIndex.HUNDRED
        )

        related_items = [item for item in items if item.item.gid == msg.object_gid]
        requests_modify_price: list[ExchangeObjectModifyPricedRequest] = []
        for item in related_items:
            items.remove(item)
            if item.item.quantity == 1 and item.price != price_for_one:
                price = price_for_one - 1
            elif item.item.quantity == 10 and item.price != price_for_ten:
                price = price_for_ten - 1
            elif item.item.quantity == 100 and item.price != price_for_hundred:
                price = price_for_hundred - 1
            else:
                continue
            if price <= 0:
                continue
            if (
                item.item.uid
                not in BID_SELLER_ITEM_BY_UID_BY_PLAYER_ID[
                    self.game_state.player.character_id
                ]
            ):
                self.logger.info(
                    f"item {item.item.uid} not in bid seller anymore, skip"
                )
                continue
            requests_modify_price.append(
                ExchangeObjectModifyPricedRequest(
                    object_uid=item.item.uid, quantity=item.item.quantity, price=price
                )
            )

        if len(requests_modify_price) == 0:
            self.choose_and_update_item_price(items)
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

            self.run_timer(VERY_SMALL_RANGE, send_all_modify_price_req)

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
        self.run_timer(
            VERY_SMALL_RANGE, lambda: self.choose_and_update_item_price(items)
        )

    def leave_all_dialogs(self):
        request = DialogLeaveRequest()
        self.event_manager.send(request)
