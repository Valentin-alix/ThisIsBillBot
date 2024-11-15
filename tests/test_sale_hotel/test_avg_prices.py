import unittest

from src.controller.scraping_d3_client.scraping_d3_client.models.quantity_enum import (
    QuantityEnum,
)
from src.core.logic.sale_hotel.price import get_price_for_sale_hotel


class TestAvgPrice(unittest.TestCase):
    def test_get_price_for_sale_hotel(self):
        min_prices_array = [
            ([50, 500, 0, 500_000], QuantityEnum.VALUE_1000),
            ([50, 500, 0, 500_000], QuantityEnum.VALUE_100),
            ([0, 25000, 0, 500_000], QuantityEnum.VALUE_100),
            ([10, 100, 1000, 5000], QuantityEnum.VALUE_1000),
        ]

        for min_prices, quantity_value in min_prices_array:
            print(get_price_for_sale_hotel(min_prices, quantity_value))
