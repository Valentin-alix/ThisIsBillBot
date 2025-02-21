from collections import defaultdict
from collections.abc import Mapping
from unittest.mock import MagicMock

import pytest
from datas.protos.non_obf.game.common_pb2 import ObjectItem, ObjectItemInventory
from dofus_unity_reader.enums.category_item_enum import CategoryEnum

from src.core.engine.economy.quantity_enum import QuantityEnum, QuantityIndex
from src.core.engine.economy.sale_hotel import (
    choose_quantity_to_sell,
    get_item_gids_to_sell,
    is_interesting_item_to_sell,
)
from tests.fixtures.data import (
    make_item_data,
    make_item_type_data,
)
from tests.fixtures.inventory import make_inventory_item


class TestSaleHotel:
    @pytest.mark.parametrize(
        ("item", "avg_prices", "expected"),
        [
            (ObjectItem(gid=1, quantity=0), {1: 1000.0}, False),
            (ObjectItem(gid=2, quantity=99), {2: 499.0}, False),
            (ObjectItem(gid=3, quantity=100), {3: 499.0}, True),
            (ObjectItem(gid=4, quantity=9), {4: 4999.0}, False),
            (ObjectItem(gid=5, quantity=10), {5: 4999.0}, True),
            (ObjectItem(gid=6, quantity=1), {6: 5000.0}, True),
        ],
    )
    def test_is_interesting_item_to_sell_thresholds(
        self,
        item: ObjectItem,
        avg_prices: dict[int, float],
        expected: bool,
    ) -> None:
        assert is_interesting_item_to_sell(item, avg_prices) is expected

    def test_choose_quantity_to_sell_protector_drop_always_returns_one(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(
            "src.core.engine.economy.sale_hotel.PROTECTOR_DROP_ITEM_IDS",
            {999},
        )

        assert choose_quantity_to_sell(
            ObjectItem(gid=999, quantity=5000),
            {999: 1.0},
        ) == (QuantityEnum.VALUE_1, QuantityIndex.ONE)

    @pytest.mark.parametrize(
        ("item", "avg_prices", "expected"),
        [
            (
                ObjectItem(gid=1, quantity=1000),
                {1: 999.0},
                (QuantityEnum.VALUE_1000, QuantityIndex.THOUSAND),
            ),
            (
                ObjectItem(gid=2, quantity=100),
                {2: 9999.0},
                (QuantityEnum.VALUE_100, QuantityIndex.HUNDRED),
            ),
            (
                ObjectItem(gid=3, quantity=10),
                {3: 99999.0},
                (QuantityEnum.VALUE_10, QuantityIndex.TEN),
            ),
            (
                ObjectItem(gid=4, quantity=9),
                {4: 10.0},
                (QuantityEnum.VALUE_1, QuantityIndex.ONE),
            ),
        ],
    )
    def test_choose_quantity_to_sell_thresholds(
        self,
        item: ObjectItem,
        avg_prices: dict[int, float],
        expected: tuple[QuantityEnum, QuantityIndex],
    ) -> None:
        assert choose_quantity_to_sell(item, avg_prices) == expected

    def test_get_item_gids_to_sell_requires_guild_chest_mapping(
        self,
        logger: MagicMock,
    ) -> None:
        with pytest.raises(ValueError):
            get_item_gids_to_sell(
                can_access_guild_chest=True,
                is_sub=True,
                bank_object_by_gid={},
                item_sell_quantity_by_gid=defaultdict(int),
                category=CategoryEnum.RESOURCES,
                logger=logger,
                avg_price_by_gid={},
            )

    def test_get_item_gids_to_sell_filters_and_sorts_bank_items(
        self,
        monkeypatch: pytest.MonkeyPatch,
        logger: MagicMock,
    ) -> None:
        self._patch_data_reader(
            monkeypatch,
            item_by_id={
                100: make_item_data(gid=100, type_id=1, level=50),
                101: make_item_data(gid=101, type_id=1, level=40),
                102: make_item_data(gid=102, type_id=2, level=40),
                103: make_item_data(gid=103, type_id=1, level=80),
                104: make_item_data(gid=104, type_id=None, level=10),
                105: make_item_data(gid=105, type_id=1, level=30),
            },
            item_type_by_id={
                1: make_item_type_data(
                    type_id=1,
                    category_id=CategoryEnum.RESOURCES,
                ),
                2: make_item_type_data(
                    type_id=2,
                    category_id=CategoryEnum.EQUIPMENT,
                ),
            },
        )
        self._patch_deterministic_random(monkeypatch)
        self._patch_weight_by_gid(monkeypatch, {100: 50.0, 101: 80.0})

        result = get_item_gids_to_sell(
            can_access_guild_chest=False,
            is_sub=False,
            bank_object_by_gid={
                100: make_inventory_item(100, 100),
                101: make_inventory_item(101, 200),
                102: make_inventory_item(102, 200),
                103: make_inventory_item(103, 200),
                104: make_inventory_item(104, 200),
                105: make_inventory_item(105, 1),
            },
            item_sell_quantity_by_gid=defaultdict(int),
            category=CategoryEnum.RESOURCES,
            logger=logger,
            avg_price_by_gid={
                100: 600.0,
                101: 6000.0,
                102: 6000.0,
                103: 6000.0,
                104: 6000.0,
                105: 100.0,
            },
        )

        assert result == [101, 100]

    def test_get_item_gids_to_sell_uses_guild_chest_items_and_sellable_filter(
        self,
        monkeypatch: pytest.MonkeyPatch,
        logger: MagicMock,
    ) -> None:
        self._patch_data_reader(
            monkeypatch,
            item_by_id={
                200: make_item_data(gid=200, type_id=1, level=20),
                201: make_item_data(gid=201, type_id=1, level=20),
            },
            item_type_by_id={
                1: make_item_type_data(
                    type_id=1,
                    category_id=CategoryEnum.RESOURCES,
                ),
            },
        )
        self._patch_deterministic_random(monkeypatch)
        self._patch_weight_by_gid(monkeypatch, {200: 10.0})

        monkeypatch.setattr(
            "src.core.engine.economy.sale_hotel.SELLABLE_ITEMS",
            {200},
        )

        result = get_item_gids_to_sell(
            can_access_guild_chest=True,
            is_sub=True,
            bank_object_by_gid={999: make_inventory_item(999, 100)},
            item_sell_quantity_by_gid=defaultdict(int),
            category=CategoryEnum.RESOURCES,
            logger=logger,
            avg_price_by_gid={
                200: 1000.0,
                201: 1000.0,
            },
            guild_chest_items_by_gid={
                200: make_inventory_item(200, 100),
                201: make_inventory_item(201, 100),
            },
        )

        assert result == [200]

    def _patch_data_reader(
        self,
        monkeypatch: pytest.MonkeyPatch,
        *,
        item_by_id: Mapping[int, object],
        item_type_by_id: Mapping[int, object],
    ) -> None:
        mock_data_reader = MagicMock()
        mock_data_reader.item_by_id = item_by_id
        mock_data_reader.item_type_by_id = item_type_by_id

        monkeypatch.setattr(
            "src.core.engine.economy.sale_hotel.DataReader",
            lambda: mock_data_reader,
        )

    def _patch_deterministic_random(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        def not_random_int(_min_value: int, _max_value: int) -> float:
            return 1.0

        monkeypatch.setattr(
            "src.core.engine.economy.sale_hotel.random.uniform", not_random_int
        )

    def _patch_weight_by_gid(
        self,
        monkeypatch: pytest.MonkeyPatch,
        weights_by_gid: Mapping[int, float],
    ) -> None:
        def get_weight(
            gid: int,
            _avg_price_by_gid: dict[int, float],
            _item_by_gid_in_storage: dict[int, ObjectItemInventory],
            _item_sell_quantity_by_gid: defaultdict[int, int],
        ) -> float:
            assert gid in weights_by_gid
            return weights_by_gid[gid]

        monkeypatch.setattr(
            "src.core.engine.economy.sale_hotel.get_weight_collectable_for_sale_hotel",
            get_weight,
        )
