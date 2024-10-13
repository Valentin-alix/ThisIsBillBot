import unittest

from src.core.controller.sale_hotel import SaleHotelController


class TestAvgPrice(unittest.TestCase):
    def test_get_prices(self):
        avg_price = SaleHotelController().get_avg_price_by_gid()
        print(avg_price)

        SaleHotelController().add_multiple_avg_price_by_gid([(10, 10)])
        avg_price = SaleHotelController().get_avg_price_by_gid()
        print(avg_price)
