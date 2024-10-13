import unittest

from src.core.controller.sale_hotel import SaleHotelController


class TestAvgPrice(unittest.TestCase):
    def test_get_prices(self):
        avg_price_by_server = SaleHotelController().get_avg_price_by_gid_by_server()
        print(avg_price_by_server)

        SaleHotelController().add_multiple_avg_price_by_gid_by_server([(10, 10, -1)])
        avg_price_by_server = SaleHotelController().get_avg_price_by_gid_by_server()
        print(avg_price_by_server)
