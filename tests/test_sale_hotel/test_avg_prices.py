import pytest
from dofus_unity_reader.game_constants.sale_hotel import QuantityEnum

from src.core.engine.economy.sale_hotel import get_price_for_sale_hotel


class TestAvgPrice:
    @pytest.mark.parametrize(
        ("min_prices", "quantity_value", "expected_price"),
        [
            ([50, 500, 0, 500_000], QuantityEnum.VALUE_1000, 50_000),
            ([50, 500, 0, 500_000], QuantityEnum.VALUE_100, 5_000),
            ([0, 25_000, 0, 500_000], QuantityEnum.VALUE_100, 250_000),
            ([10, 100, 1_000, 5_000], QuantityEnum.VALUE_1000, 5_000),
        ],
    )
    def test_get_price_for_sale_hotel(
        self,
        min_prices: list[int],
        quantity_value: QuantityEnum,
        expected_price: int,
    ) -> None:
        assert get_price_for_sale_hotel(min_prices, quantity_value) == expected_price
