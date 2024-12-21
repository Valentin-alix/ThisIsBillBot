import unittest
from collections import defaultdict
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from dofus_unity_reader.enums.category_item_enum import CategoryEnum
from datas.protos.non_obf.game.common_pb2 import ObjectItem, ObjectItemInventory

from src.core.engine.economy.quantity_enum import QuantityEnum, QuantityIndex
from src.core.engine.economy.sale_hotel import (
    choose_quantity_to_sell,
    get_item_gids_to_sell,
    is_interesting_item_to_sell,
)


def _make_inventory_item(gid: int, quantity: int) -> ObjectItemInventory:
    return ObjectItemInventory(item=ObjectItem(gid=gid, quantity=quantity))


class TestSaleHotel(unittest.TestCase):
    def setUp(self) -> None:
        self.logger = MagicMock()

    def test_is_interesting_item_to_sell_thresholds(self) -> None:
        test_cases = [
            (ObjectItem(gid=1, quantity=0), {1: 1000.0}, False),
            (ObjectItem(gid=2, quantity=99), {2: 499.0}, False),
            (ObjectItem(gid=3, quantity=100), {3: 499.0}, True),
            (ObjectItem(gid=4, quantity=9), {4: 4999.0}, False),
            (ObjectItem(gid=5, quantity=10), {5: 4999.0}, True),
            (ObjectItem(gid=6, quantity=1), {6: 5000.0}, True),
        ]

        for item, avg_prices, expected in test_cases:
            with self.subTest(gid=item.gid, quantity=item.quantity):
                self.assertEqual(
                    is_interesting_item_to_sell(item, avg_prices),
                    expected,
                )

    @patch("src.core.engine.economy.sale_hotel.PROTECTOR_DROP_ITEM_IDS", {999})
    def test_choose_quantity_to_sell_protector_drop_always_returns_one(self) -> None:
        quantity, index = choose_quantity_to_sell(
            ObjectItem(gid=999, quantity=5000),
            {999: 1.0},
        )

        self.assertEqual(quantity, QuantityEnum.VALUE_1)
        self.assertEqual(index, QuantityIndex.ONE)

    def test_choose_quantity_to_sell_thresholds(self) -> None:
        test_cases = [
            (
                ObjectItem(gid=1, quantity=1000),
                {1: 999.0},
                QuantityEnum.VALUE_1000,
                QuantityIndex.THOUSAND,
            ),
            (
                ObjectItem(gid=2, quantity=100),
                {2: 9999.0},
                QuantityEnum.VALUE_100,
                QuantityIndex.HUNDRED,
            ),
            (
                ObjectItem(gid=3, quantity=10),
                {3: 99999.0},
                QuantityEnum.VALUE_10,
                QuantityIndex.TEN,
            ),
            (
                ObjectItem(gid=4, quantity=9),
                {4: 10.0},
                QuantityEnum.VALUE_1,
                QuantityIndex.ONE,
            ),
        ]

        for item, avg_prices, expected_quantity, expected_index in test_cases:
            with self.subTest(gid=item.gid, quantity=item.quantity):
                quantity, index = choose_quantity_to_sell(item, avg_prices)
                self.assertEqual(quantity, expected_quantity)
                self.assertEqual(index, expected_index)

    def test_get_item_gids_to_sell_requires_guild_chest_mapping(self) -> None:
        with self.assertRaises(ValueError):
            get_item_gids_to_sell(
                can_access_guild_chest=True,
                is_sub=True,
                bank_object_by_gid={},
                item_sell_quantity_by_gid=defaultdict(int),
                category=CategoryEnum.RESOURCES,
                logger=self.logger,
                avg_price_by_gid={},
            )

    @patch("src.core.engine.economy.sale_hotel.random.uniform", return_value=1.0)
    @patch("src.core.engine.economy.sale_hotel.get_weight_collectable_for_sale_hotel")
    @patch("src.core.engine.economy.sale_hotel.DataReader")
    def test_get_item_gids_to_sell_filters_and_sorts_bank_items(
        self,
        mock_data_reader_class: MagicMock,
        mock_get_weight: MagicMock,
        _mock_random: MagicMock,
    ) -> None:
        mock_data_reader = MagicMock()
        mock_data_reader.item_by_id = {
            100: SimpleNamespace(typeId=1, level=50),
            101: SimpleNamespace(typeId=1, level=40),
            102: SimpleNamespace(typeId=2, level=40),
            103: SimpleNamespace(typeId=1, level=80),
            104: SimpleNamespace(typeId=None, level=10),
            105: SimpleNamespace(typeId=1, level=30),
        }
        mock_data_reader.item_type_by_id = {
            1: SimpleNamespace(categoryId=CategoryEnum.RESOURCES),
            2: SimpleNamespace(categoryId=CategoryEnum.EQUIPMENT),
        }
        mock_data_reader_class.return_value = mock_data_reader

        bank_items = {
            100: _make_inventory_item(100, 100),
            101: _make_inventory_item(101, 200),
            102: _make_inventory_item(102, 200),
            103: _make_inventory_item(103, 200),
            104: _make_inventory_item(104, 200),
            105: _make_inventory_item(105, 1),
        }

        def get_weight(
            gid: int,
            _avg_price_by_gid: dict[int, float],
            _item_by_gid_in_storage: dict[int, ObjectItemInventory],
            _item_sell_quantity_by_gid: defaultdict[int, int],
        ) -> float:
            return {100: 50.0, 101: 80.0}[gid]

        mock_get_weight.side_effect = get_weight

        result = get_item_gids_to_sell(
            can_access_guild_chest=False,
            is_sub=False,
            bank_object_by_gid=bank_items,
            item_sell_quantity_by_gid=defaultdict(int),
            category=CategoryEnum.RESOURCES,
            logger=self.logger,
            avg_price_by_gid={
                100: 600.0,
                101: 6000.0,
                102: 6000.0,
                103: 6000.0,
                104: 6000.0,
                105: 100.0,
            },
        )

        self.assertEqual(result, [101, 100])
        self.logger.info.assert_any_call("count item in storage : 6")
        self.logger.info.assert_any_call("count item to sell : 2")

    @patch("src.core.engine.economy.sale_hotel.SELLABLE_ITEMS", {200})
    @patch("src.core.engine.economy.sale_hotel.random.uniform", return_value=1.0)
    @patch("src.core.engine.economy.sale_hotel.get_weight_collectable_for_sale_hotel")
    @patch("src.core.engine.economy.sale_hotel.DataReader")
    def test_get_item_gids_to_sell_uses_guild_chest_items_and_sellable_filter(
        self,
        mock_data_reader_class: MagicMock,
        mock_get_weight: MagicMock,
        _mock_random: MagicMock,
    ) -> None:
        mock_data_reader = MagicMock()
        mock_data_reader.item_by_id = {
            200: SimpleNamespace(typeId=1, level=20),
            201: SimpleNamespace(typeId=1, level=20),
        }
        mock_data_reader.item_type_by_id = {
            1: SimpleNamespace(categoryId=CategoryEnum.RESOURCES),
        }
        mock_data_reader_class.return_value = mock_data_reader

        def get_weight(
            gid: int,
            _avg_price_by_gid: dict[int, float],
            _item_by_gid_in_storage: dict[int, ObjectItemInventory],
            _item_sell_quantity_by_gid: defaultdict[int, int],
        ) -> float:
            return {200: 10.0}[gid]

        mock_get_weight.side_effect = get_weight

        result = get_item_gids_to_sell(
            can_access_guild_chest=True,
            is_sub=True,
            bank_object_by_gid={999: _make_inventory_item(999, 100)},
            item_sell_quantity_by_gid=defaultdict(int),
            category=CategoryEnum.RESOURCES,
            logger=self.logger,
            avg_price_by_gid={200: 1000.0, 201: 1000.0},
            guild_chest_items_by_gid={
                200: _make_inventory_item(200, 100),
                201: _make_inventory_item(201, 100),
            },
        )

        self.assertEqual(result, [200])
