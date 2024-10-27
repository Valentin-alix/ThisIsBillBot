from collections import defaultdict
import math
import random
from d3_mapping.resources.protos.game.common_pb2 import ObjectItem, ObjectItemInventory
from data_center.data_reader import DataReader
from enums.category_item_enum import CategoryEnum
from scraping_d3_client.scraping_d3_client.models.quantity_enum import QuantityEnum
from scraping_d3_client.scraping_d3_client.models.quantity_enum import QuantityIndex
from src.common.logger import Logger
from src.controller.sale_hotel import SaleHotelController
from src.core.config.sale_hotel import MAX_QUANTITY_ON_SELL
from src.core.config.storage import (
    SELLABLE_ITEMS,
    PROTECTOR_DROP_ITEM_IDS,
)
from src.core.logic.farmer.weight_item import get_weight_item_for_sale_hotel
from src.core.states.guild_chest_state import CHEST_OBJECT_BY_GID_BY_TAB


def get_item_gids_to_sell(
    can_access_guild_chest: bool,
    is_sub: bool,
    bank_object_by_gid: dict[int, ObjectItemInventory],
    item_sell_quantity_by_gid: defaultdict[int, int],
    category: CategoryEnum,
    logger: Logger,
):
    if can_access_guild_chest:
        item_by_gid_in_storage = {
            gid: item
            for tab in CHEST_OBJECT_BY_GID_BY_TAB.values()
            for gid, item in tab.items()
        }
    else:
        item_by_gid_in_storage = bank_object_by_gid

    logger.info(f"count item in storage : {len(item_by_gid_in_storage)}")

    def is_valid_item_to_sell(gid: int, object_item: ObjectItemInventory):
        item_data = DataReader().item_by_id[gid]
        if not item_data.typeId:
            return False
        if not (is_sub or (item_data.level or 0) <= 60):
            return False
        if gid not in SELLABLE_ITEMS:
            return False
        if not is_interesting_item_to_sell(object_item.item):
            return False
        return DataReader().item_type_by_id[item_data.typeId].categoryId == category

    item_gids_to_sell = [
        item_gid
        for item_gid, item in item_by_gid_in_storage.items()
        if is_valid_item_to_sell(item_gid, item)
    ]

    logger.info(f"count item to sell : {len(item_gids_to_sell)}")

    avg_price_by_gid = SaleHotelController().get_avg_price_by_gid()

    item_gids_to_sell.sort(
        key=lambda item_gid: random.randint(1, 10)
        * get_weight_item_for_sale_hotel(
            item_gid, avg_price_by_gid, item_by_gid_in_storage
        )
        / (1 + item_sell_quantity_by_gid.get(item_gid, 0)),
        reverse=True,
    )

    return item_gids_to_sell


def is_interesting_item_to_sell(object_item: ObjectItem):
    if object_item.quantity <= 0:
        return False
    avg_price = SaleHotelController().get_avg_price_by_gid()[object_item.gid]
    if avg_price < 5_000 and object_item.quantity < 100:
        return False
    elif avg_price < 50_000 and object_item.quantity < 10:
        return False
    return True


def choose_quantity_to_sell(item: ObjectItem):
    if item.gid in PROTECTOR_DROP_ITEM_IDS:
        return QuantityEnum.VALUE_1, QuantityIndex.ONE

    avg_price = SaleHotelController().get_avg_price_by_gid()[item.gid]
    if item.quantity >= 1000 and avg_price < 1_000:
        quantity_to_sell = QuantityEnum.VALUE_1000
        quantity_index = QuantityIndex.THOUSAND
    elif item.quantity >= 100 and avg_price < 10_000:
        quantity_to_sell = QuantityEnum.VALUE_100
        quantity_index = QuantityIndex.HUNDRED
    elif item.quantity >= 10 and avg_price < 100_000:
        quantity_to_sell = QuantityEnum.VALUE_10
        quantity_index = QuantityIndex.TEN
    else:
        quantity_to_sell = QuantityEnum.VALUE_1
        quantity_index = QuantityIndex.ONE

    return quantity_to_sell, quantity_index


def get_max_quantity_sell(gid: int) -> int:
    if gid in PROTECTOR_DROP_ITEM_IDS:
        return 2

    avg_price = SaleHotelController().get_avg_price_by_gid()[gid]
    return math.ceil(MAX_QUANTITY_ON_SELL / (avg_price / 1000 + 1))


def get_price_for_sale_hotel(
    prices: list[int], quantity_index: QuantityIndex, quantity: QuantityEnum
):
    avg_price = get_average_price_for_description(prices) * quantity
    min_price = prices[quantity_index]
    if min_price == 0:
        return avg_price
    return min(avg_price, min_price)


def get_average_price_for_description(prices: list[int]) -> int:
    sum_price = 0
    valid_quantity = 0
    if prices[QuantityIndex.ONE] != 0:
        sum_price += prices[QuantityIndex.ONE]
        valid_quantity += 1
    if prices[QuantityIndex.TEN] != 0:
        sum_price += prices[QuantityIndex.TEN]
        valid_quantity += 10
    if prices[QuantityIndex.HUNDRED] != 0:
        sum_price += prices[QuantityIndex.HUNDRED]
        valid_quantity += 100
    if prices[QuantityIndex.THOUSAND] != 0:
        sum_price += prices[QuantityIndex.THOUSAND]
        valid_quantity += 1000

    if valid_quantity == 0:
        return 0
    return sum_price // valid_quantity


if __name__ == "__main__":
    min_prices = [99_999, 4878, 35548, 368997]
    avg_price = get_average_price_for_description(min_prices)
    print(avg_price)

    print(
        get_price_for_sale_hotel(
            min_prices, QuantityIndex.HUNDRED, QuantityEnum.VALUE_100
        )
    )
