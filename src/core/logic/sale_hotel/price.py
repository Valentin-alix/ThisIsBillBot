from enum import IntEnum


class QuantityIndex(IntEnum):
    ONE = 0
    TEN = 1
    HUNDRED = 2


def get_price_for_sale_hotel(
    prices: list[int],
    quantity: QuantityIndex,
):
    if prices[quantity] == 0:
        min_price = get_average_price_for_description(prices)
    else:
        min_price = prices[quantity]
    return min_price


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
    if valid_quantity == 0:
        return 0
    return sum_price // valid_quantity
