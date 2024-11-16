import math
import random
from collections import defaultdict
from statistics import median
from typing import cast

from D3Database.data_center.data_reader import DataReader
from D3Database.enums.category_item_enum import CategoryEnum
from D3Mapping.d3_mapping.resources.protos.game.common_pb2 import (
    ObjectItem,
    ObjectItemInventory,
)
from src.controller.scraping_d3_api.scraping_d3_client.scraping_d3_client.models.quantity_enum import (
    QUANTITY_INDEX_BY_QUANTITY,
    QuantityEnum,
    QuantityIndex,
)
from src.core.config import MAX_QUANTITY_ON_SELL
from src.core.engine.weights.harvester.weight_collectable import (
    get_weight_collectable_for_sale_hotel,
)
from src.core.game_constants import PROTECTOR_DROP_ITEM_IDS, SELLABLE_ITEMS
from src.services.logging.logger import Logger


def get_item_gids_to_sell(
    can_access_guild_chest: bool,
    is_sub: bool,
    bank_object_by_gid: dict[int, ObjectItemInventory],
    item_sell_quantity_by_gid: defaultdict[int, int],
    category: CategoryEnum,
    logger: Logger,
    avg_price_by_gid: dict[int, float],
    guild_chest_object_by_gid_by_tab: dict[int, dict[int, ObjectItemInventory]]
    | None = None,
):
    if can_access_guild_chest:
        if guild_chest_object_by_gid_by_tab is None:
            raise ValueError(
                "guild_chest_object_by_gid_by_tab required when can_access_guild_chest=True"
            )
        item_by_gid_in_storage = {
            gid: item
            for tab in guild_chest_object_by_gid_by_tab.values()
            for gid, item in tab.items()
        }
    else:
        item_by_gid_in_storage = bank_object_by_gid

    logger.info(f"count item in storage : {len(item_by_gid_in_storage)}")

    def is_valid_item_to_sell(
        gid: int, object_item: ObjectItemInventory, is_bank_item: bool
    ):
        item_data = DataReader().item_by_id[gid]
        if not item_data.typeId:
            return False
        if not (is_sub or (item_data.level or 0) <= 60):
            return False
        if not is_bank_item and gid not in SELLABLE_ITEMS:
            return False
        if not is_interesting_item_to_sell(object_item.item, avg_price_by_gid):
            return False
        return DataReader().item_type_by_id[item_data.typeId].categoryId == category

    item_gids_to_sell = [
        item_gid
        for item_gid, item in item_by_gid_in_storage.items()
        if is_valid_item_to_sell(item_gid, item, not can_access_guild_chest)
    ]

    logger.info(f"count item to sell : {len(item_gids_to_sell)}")

    item_gids_to_sell.sort(
        key=lambda item_gid: random.randint(1, 5)
        * get_weight_collectable_for_sale_hotel(
            item_gid,
            avg_price_by_gid,
            item_by_gid_in_storage,
            item_sell_quantity_by_gid,
        ),
        reverse=True,
    )

    return item_gids_to_sell


def is_interesting_item_to_sell(
    object_item: ObjectItem,
    avg_price_by_gid: dict[int, float],
):
    if object_item.quantity <= 0:
        return False
    avg_price = avg_price_by_gid.get(object_item.gid, 1)
    if avg_price < 500 and object_item.quantity < 100:
        return False
    elif avg_price < 5_000 and object_item.quantity < 10:
        return False
    return True


def choose_quantity_to_sell(
    item: ObjectItem,
    avg_price_by_gid: dict[int, float],
):
    if item.gid in PROTECTOR_DROP_ITEM_IDS:
        return QuantityEnum.VALUE_1, QuantityIndex.ONE

    avg_price = avg_price_by_gid[item.gid]
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
        return 1
    return MAX_QUANTITY_ON_SELL


PRICE_LOW_RATIO = 0.5
PRICE_HIGH_RATIO = 2.0


def get_price_for_sale_hotel(
    min_prices: list[int],
    target_lot: QuantityEnum,
) -> int:
    unit_prices: list[float | None] = []
    valid_indexes: list[int] = []

    for index, (current_price, current_lot) in enumerate(zip(min_prices, QuantityEnum)):
        if current_price > 0:
            unit_prices.append(current_price / current_lot)
            valid_indexes.append(index)
        else:
            unit_prices.append(None)

    if not valid_indexes:
        return 0

    filtered_unit_prices: list[float] = [
        cast(float, unit_prices[index]) for index in valid_indexes
    ]
    median_raw = median(filtered_unit_prices)

    accepted_indexes: list[int] = []

    for index in valid_indexes:
        unit_price = cast(float, unit_prices[index])
        ratio = unit_price / median_raw
        if PRICE_LOW_RATIO <= ratio <= PRICE_HIGH_RATIO:
            accepted_indexes.append(index)

    if not accepted_indexes:
        closest_index = min(
            valid_indexes,
            key=lambda index: abs(cast(float, unit_prices[index]) - median_raw),
        )
        accepted_indexes = [closest_index]

    cleaned_unit_price = median(
        [cast(float, unit_prices[index]) for index in accepted_indexes]
    )

    lot_index_by_quantity = QUANTITY_INDEX_BY_QUANTITY[target_lot]
    curr_min_price_lot = (
        min_prices[lot_index_by_quantity]
        if min_prices[lot_index_by_quantity] > 0
        else float("inf")
    )

    return int(min(cleaned_unit_price * target_lot, curr_min_price_lot))


if __name__ == "__main__":
    # Example usage - requires avg_price_by_gid injected
    test_avg_prices = {533: 1000.0}
    print(
        is_interesting_item_to_sell(
            ObjectItem(uid=1, quantity=561, gid=533), test_avg_prices
        )
    )
    print(math.ceil(MAX_QUANTITY_ON_SELL / ((1000 / 500) + 1)))
    min_prices = [50, 500, 5000, 500_000]
    print(get_price_for_sale_hotel(min_prices, QuantityEnum.VALUE_1000))
