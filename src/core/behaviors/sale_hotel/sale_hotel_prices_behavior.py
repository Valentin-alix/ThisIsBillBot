import math
from dataclasses import dataclass, field
from enum import StrEnum, auto
from functools import partial
from typing import Iterable

from datas.protos.non_obf.game.common_pb2 import ObjectItem
from datas.protos.non_obf.game.exchange_pb2 import (
    ExchangeBidHouseItemRemovedEvent,
    ExchangeBidHousePriceRequest,
    ExchangeBidHouseSearchRequest,
    ExchangeBidPriceEvent,
    ExchangeBidSellerStartedEvent,
    ExchangeLeaveEvent,
    ExchangeObjectModifyPricedRequest,
    ExchangeObjectMovePricedRequest,
)
from datas.protos.non_obf.game.inventory_pb2 import (
    InventoryWeightEvent,
)
from dofus_unity_reader.data_center.data_reader import DataReader
from dofus_unity_reader.data_center.i18n import I18N
from dofus_unity_reader.enums.category_item_enum import CategoryEnum

from src.controller.sale_hotel import SaleHotelController
from src.core.behaviors.dialog_handler_behavior import DialogHandlerBehavior
from src.core.behaviors.sale_hotel.enter_sale_hotel_sell_behavior import (
    EnterSaleHotelSellBehavior,
)
from src.core.behaviors.storage.loads.load_from_bank_behavior import (
    LoadFromBankBehavior,
)
from src.core.behaviors.storage.loads.load_from_guild_chest_behavior import (
    LoadFromGuildChestBehavior,
)
from src.core.behaviors.storage.loads.load_item_request import LoadItemInfo
from src.core.config import (
    BASE_RANGE,
    MIN_KAMAS_TO_GO_SALE_HOTEL,
    SALE_HOTEL_LISTING_FEE,
    SMALL_RANGE,
    TINY_RANGE,
)
from src.core.engine.economy.quantity_enum import QuantityEnum
from src.core.engine.economy.sale_hotel import (
    choose_quantity_to_sell,
    get_item_gids_to_sell,
    get_max_quantity_sell,
    get_price_for_sale_hotel,
    is_interesting_item_to_sell,
)
from src.core.states.guild_chest_state import TAB_BY_GID
from src.exceptions import UnexpectedStateException


class SaleHotelErrorCode(StrEnum):
    NOT_ENOUGH_KAMAS = auto()


@dataclass
class SaleHotelPricesBehavior(DialogHandlerBehavior):
    enter_sale_hotel_sell_behavior: EnterSaleHotelSellBehavior
    load_from_guild_chest_behavior: LoadFromGuildChestBehavior
    load_from_bank_behavior: LoadFromBankBehavior

    categories: set[CategoryEnum] = field(init=False, default_factory=set[CategoryEnum])
    _curr_category: CategoryEnum = field(init=False, default=CategoryEnum.RESOURCES)
    _remaining_quantity_by_uid: dict[int, int] = field(
        init=False, default_factory=dict[int, int]
    )
    _item_to_sells_in_inventory: list[ObjectItem] = field(
        init=False, default_factory=list[ObjectItem]
    )
    _item_ids_to_sell: list[int] = field(init=False, default_factory=list[int])
    _items_in_sale_hotel: list[ExchangeBidSellerStartedEvent.ItemToSellInBid] = field(
        init=False,
        default_factory=list[ExchangeBidSellerStartedEvent.ItemToSellInBid],
    )
    _load_items_infos: list[LoadItemInfo] = field(
        init=False, default_factory=list[LoadItemInfo]
    )

    def run(self) -> None:
        self.categories = {CategoryEnum.RESOURCES, CategoryEnum.CONSUMABLES}

        if self.game_state.inventory.kamas < MIN_KAMAS_TO_GO_SALE_HOTEL:
            self.logger.warning(
                "Player does not have enough kamas, skipping sale hotel"
            )
            return self.finish()

        self.sell_next_category()

    def sell_next_category(self) -> None:
        if len(self.categories) == 0:
            return self.finish()

        self._curr_category = self.categories.pop()

        item_sell_quantity_by_gid = SaleHotelController().get_item_sell_quantity_by_gid(
            self.game_state.player.server_id
        )
        avg_price_by_gid = SaleHotelController().get_avg_price_by_gid(
            self.game_state.player.server_id
        )

        self._item_ids_to_sell = get_item_gids_to_sell(
            self.game_state.guild_chest.can_access_guild_chest,
            self.game_state.player.is_sub,
            self.game_state.inventory.get_bank_objects_by_gid(),
            item_sell_quantity_by_gid,
            self._curr_category,
            self.logger,
            avg_price_by_gid,
            self.game_state.guild_chest.storage.get_all_items_by_gid(),
        )

        if len(self._item_ids_to_sell) == 0:
            return self.sell_next_category()

        self.logger.info(
            f"Item to sells : {[I18N().name_by_id.get(DataReader().item_by_id[gid].nameId, f'Unknown {gid}') for gid in self._item_ids_to_sell]}"
        )

        self._load_items_infos: list[LoadItemInfo] = []
        for item_gid in self._item_ids_to_sell:
            max_quantity_sell = get_max_quantity_sell(item_gid)
            remaining_qty = min(
                max(max_quantity_sell - item_sell_quantity_by_gid.get(item_gid, 0), 0),
                math.floor(max_quantity_sell / 4),
            )
            load_item_info = LoadItemInfo(
                item_gid=item_gid,
                remaining_quantity=remaining_qty,
                tab=TAB_BY_GID.get(item_gid, 0),
            )
            self._load_items_infos.append(load_item_info)

        self.load_items()

    def load_items(self) -> None:
        self.logger.info(f"Gonna load and sell : {self._load_items_infos}")
        if self.game_state.guild_chest.can_access_guild_chest:
            self.load_from_guild_chest_behavior.start(
                callback=self.on_loaded_behavior_finished,
                parent=self,
                load_items_infos=self._load_items_infos,
            )
        else:
            self.load_from_bank_behavior.start(
                callback=self.on_loaded_behavior_finished,
                parent=self,
                load_items_infos=self._load_items_infos,
            )

    def on_loaded_behavior_finished(
        self, error_code: str | None, load_items_infos: list[LoadItemInfo]
    ) -> None:
        self.raise_if_error(error_code)
        self._load_items_infos = load_items_infos
        self.enter_sale_hotel_sell_behavior.start(
            callback=self.on_enter_sale_hotel_sell_behavior_finished,
            parent=self,
            category=self._curr_category,
        )

    def on_enter_sale_hotel_sell_behavior_finished(
        self,
        error_code: str | None,
        items: Iterable[ExchangeBidSellerStartedEvent.ItemToSellInBid],
    ) -> None:
        self.raise_if_error(error_code)
        self._items_in_sale_hotel = list(items)
        self.sell_inventory()

    def sell_inventory(self) -> None:
        self._item_to_sells_in_inventory = [
            object.item
            for object in self.game_state.inventory.objects_by_uid.values()
            if object.item.gid in self._item_ids_to_sell
        ]
        self._remaining_quantity_by_uid = {
            item.uid: item.quantity for item in self._item_to_sells_in_inventory
        }
        self.logger.info(
            f"Gonna sell in inventory : {[item.gid for item in self._item_to_sells_in_inventory]}"
        )
        self.create_all_prices()

    def create_all_prices(self) -> None:
        while True:
            if len(self._item_to_sells_in_inventory) == 0:
                if len(self._load_items_infos) == 0:
                    self.logger.info("No more item to sell, lets update prices")
                    return self.update_all_prices()

                self.event_manager.on(
                    ExchangeLeaveEvent,
                    callback=lambda _: self.load_items(),
                    originator=self,
                    once=True,
                )
                return self.leave_dialog()

            next_item = self._item_to_sells_in_inventory.pop()
            if is_interesting_item_to_sell(
                next_item,
                SaleHotelController().get_avg_price_by_gid(
                    self.game_state.player.server_id
                ),
            ):
                break

        self.logger.info(
            f"Sell item {next_item.gid} with quantity {next_item.quantity}"
        )
        self.event_manager.on(
            ExchangeBidHouseSearchRequest,
            partial(
                self.on_exchange_bid_house_search_request_follow,
                next_item=next_item,
            ),
            originator=self,
        )
        self.run_timer(SMALL_RANGE, lambda: self.open_item(next_item.gid))

    def open_item(self, item_gid: int) -> None:
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
        next_item: ObjectItem,
    ) -> None:
        if not msg.follow:
            return
        self.unregister_listener(
            ExchangeBidHouseSearchRequest,
            reason="Item selected for pricing, switching to price event listener",
        )
        self.event_manager.on(
            ExchangeBidPriceEvent,
            partial(
                self.on_exchange_bid_price_event_after_select_for_create_price,
                item=next_item,
            ),
            originator=self,
            once=True,
        )
        req = ExchangeBidHousePriceRequest(object_gid=msg.object_gid)
        self.event_manager.send(req)

    def on_exchange_bid_price_event_after_select_for_create_price(
        self,
        msg: ExchangeBidPriceEvent,
        item: ObjectItem,
    ) -> None:
        self.create_price(list(msg.bid_price_for_seller.minimal_prices), item)

    def create_price(self, minimal_prices: list[int], item: ObjectItem) -> None:
        server_id = self.game_state.player.server_id
        avg_price_by_gid = SaleHotelController().get_avg_price_by_gid(server_id)

        remaining = self._remaining_quantity_by_uid.get(item.uid, item.quantity)
        if not is_interesting_item_to_sell(item, avg_price_by_gid, remaining):
            return self.create_all_prices()

        quantity_to_sell, _ = choose_quantity_to_sell(item, avg_price_by_gid, remaining)

        bot_min_price = (
            SaleHotelController()
            .get_minimal_price_by_gid_and_quantity(server_id)
            .get((item.gid, quantity_to_sell))
        )
        market_price = get_price_for_sale_hotel(list(minimal_prices), quantity_to_sell)
        price_for_quantity = self._compute_price_with_undercut(
            market_price, bot_min_price
        )

        self.logger.info(
            f"Price for {quantity_to_sell} for item {item.gid} : {price_for_quantity}"
        )
        if price_for_quantity <= 0:
            return self.create_all_prices()

        if self.game_state.sale_hotel.bid_seller_condition is None:
            raise UnexpectedStateException("we should have bid seller infos")

        count_item_in_sale = len(
            SaleHotelController()
            .get_hdv_by_uid_by_player(server_id)
            .get(self.game_state.player.character_id, {})
        )
        self.logger.info(
            f"item in sale : {count_item_in_sale}, max item possible in sale : {self.game_state.sale_hotel.bid_seller_condition.max_item_per_account}"
        )
        if self.game_state.sale_hotel.is_full_object_in_sale_hotel:
            self.logger.info("Sale hotel is full of object, let's update prices")
            return self.update_all_prices()

        if (
            price_for_quantity * SALE_HOTEL_LISTING_FEE
            > self.game_state.inventory.kamas
        ):
            self.event_manager.on(
                ExchangeLeaveEvent,
                callback=lambda _: self.finish(SaleHotelErrorCode.NOT_ENOUGH_KAMAS),
                originator=self,
                once=True,
            )
            return self.leave_dialog()

        self.event_manager.on(
            InventoryWeightEvent,
            lambda _: self.on_inventory_weight_event_after_created_price(
                item=item,
                minimal_prices=minimal_prices,
            ),
            originator=self,
            once=True,
        )
        self._remaining_quantity_by_uid[item.uid] = remaining - quantity_to_sell
        self.logger.info(
            f"Remaining quantity of item {item.gid} : {self._remaining_quantity_by_uid[item.uid]}"
        )
        req = ExchangeObjectMovePricedRequest(
            object_uid=item.uid, quantity=quantity_to_sell, price=price_for_quantity
        )
        self.send_message_delayed(req, TINY_RANGE)

    def on_inventory_weight_event_after_created_price(
        self,
        item: ObjectItem,
        minimal_prices: list[int],
    ) -> None:
        if self.game_state.sale_hotel.is_full_object_in_sale_hotel:
            return self.update_all_prices()

        self.logger.info("Successfully created price, move on to next item quantity")
        self.create_price(minimal_prices=minimal_prices, item=item)

    def update_all_prices(self) -> None:
        if len(self._items_in_sale_hotel) == 0:
            self.event_manager.on(
                ExchangeLeaveEvent,
                callback=lambda _: self.sell_next_category(),
                originator=self,
                once=True,
            )
            return self.leave_dialog()
        self.logger.info("Update prices of all item in sale hotel")
        item = self._items_in_sale_hotel[0]
        self.update_item_price(item.item.gid)

    def update_item_price(self, item_gid: int) -> None:
        self.event_manager.on(
            ExchangeBidPriceEvent,
            partial(self.on_exchange_bid_price_event, item_gid=item_gid),
            originator=self,
            once=True,
        )
        self.logger.info(f"Updating item {item_gid}")
        req = ExchangeBidHousePriceRequest(object_gid=item_gid)
        self.send_message_delayed(req, SMALL_RANGE)

    def on_exchange_bid_price_event(
        self, msg: ExchangeBidPriceEvent, item_gid: int
    ) -> None:
        prices_by_quantity = self._compute_prices_by_quantity(
            list(msg.bid_price_for_seller.minimal_prices), item_gid
        )

        related_items = [
            item for item in self._items_in_sale_hotel if item.item.gid == item_gid
        ]
        price_cost: float = 0
        requests_modify_price: list[ExchangeObjectModifyPricedRequest] = []
        server_id = self.game_state.player.server_id

        for item in related_items:
            self._items_in_sale_hotel.remove(item)
            new_price = prices_by_quantity.get(QuantityEnum(item.item.quantity))
            if new_price is None or new_price == item.price or new_price <= 0:
                continue
            if item.item.uid not in SaleHotelController().get_hdv_by_uid_by_player(
                server_id
            ).get(self.game_state.player.character_id, {}):
                self.logger.info(
                    f"item {item.item.uid} not in bid seller anymore, skip"
                )
                continue
            price_cost += new_price * SALE_HOTEL_LISTING_FEE
            if price_cost > self.game_state.inventory.kamas:
                break
            requests_modify_price.append(
                ExchangeObjectModifyPricedRequest(
                    object_uid=item.item.uid,
                    quantity=item.item.quantity,
                    price=new_price,
                )
            )

        if len(requests_modify_price) == 0:
            self.logger.info("No request modify, go next item")
            self.update_all_prices()
        else:
            self.event_manager.on(
                ExchangeBidHouseItemRemovedEvent,
                partial(
                    self.on_exchange_bid_house_item_removed_event_after_updated,
                    target_uid=requests_modify_price[-1].object_uid,
                ),
                originator=self,
            )

            def send_all_modify_price_req() -> None:
                for request_modify_price in requests_modify_price:
                    self.event_manager.send(request_modify_price)

            self.run_timer(BASE_RANGE, send_all_modify_price_req)

    def on_exchange_bid_house_item_removed_event_after_updated(
        self,
        msg: ExchangeBidHouseItemRemovedEvent,
        target_uid: int,
    ) -> None:
        if msg.sell_id != target_uid:
            return
        self.unregister_listener(
            ExchangeBidHouseItemRemovedEvent,
            reason="Item removed from sale hotel, proceeding to update all prices",
        )
        self.logger.info("Update all prices after item removed")
        self.run_timer(BASE_RANGE, self.update_all_prices)

    def _compute_price_with_undercut(
        self, market_price: int, bot_min_price: int | None
    ) -> int:
        return market_price - 1 if market_price != bot_min_price else market_price

    def _compute_prices_by_quantity(
        self, minimal_prices: list[int], item_gid: int
    ) -> dict[QuantityEnum, int]:
        server_id = self.game_state.player.server_id
        bot_mins = SaleHotelController().get_minimal_price_by_gid_and_quantity(
            server_id
        )

        return {
            qty: self._compute_price_with_undercut(
                get_price_for_sale_hotel(minimal_prices, qty),
                bot_mins.get((item_gid, qty)),
            )
            for qty in QuantityEnum
        }
