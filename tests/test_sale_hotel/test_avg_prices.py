import unittest

from src.core.engine.economy.quantity_enum import QuantityEnum
from src.core.engine.economy.sale_hotel import get_price_for_sale_hotel


class TestAvgPrice(unittest.TestCase):
    def test_get_price_for_sale_hotel(self):
        min_prices_array = [
            ([50, 500, 0, 500_000], QuantityEnum.VALUE_1000, 50000),
            ([50, 500, 0, 500_000], QuantityEnum.VALUE_100, 5000),
            ([0, 25000, 0, 500_000], QuantityEnum.VALUE_100, 250000),
            ([10, 100, 1000, 5000], QuantityEnum.VALUE_1000, 5000),
        ]

        for min_prices, quantity_value, expected_price in min_prices_array:
            assert expected_price == get_price_for_sale_hotel(
                min_prices, quantity_value
            )
