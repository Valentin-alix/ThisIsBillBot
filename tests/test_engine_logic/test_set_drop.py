from types import SimpleNamespace
from typing import Callable, cast

import pytest
from datas.protos.non_obf.game.common_pb2 import ObjectItemInventory
from dofus_unity_reader.game_constants.characteristic import EffectElement

from src.core.engine.weights.fighter import set_drop
from src.core.engine.weights.fighter.set_drop import (
    choose_set_drop_sub_area_id,
    get_missing_set_drop_sub_area_ids,
)


def _reader(**attrs: object) -> Callable[[], SimpleNamespace]:
    def build() -> SimpleNamespace:
        return SimpleNamespace(**attrs)

    return build


def _const(value: object) -> Callable[..., object]:
    def fn(*_args: object) -> object:
        return value

    return fn


def _monster(object_ids: list[int], sub_areas: list[int]) -> SimpleNamespace:
    return SimpleNamespace(
        drops=[SimpleNamespace(objectId=object_id) for object_id in object_ids],
        subareas=sub_areas,
        favoriteSubareaId=sub_areas[0] if sub_areas else 0,
    )


def _owned(object_by_gid: dict[int, int]) -> dict[int, ObjectItemInventory]:
    return cast(
        dict[int, ObjectItemInventory],
        {
            uid: SimpleNamespace(item=SimpleNamespace(gid=gid))
            for uid, gid in object_by_gid.items()
        },
    )


class TestMissingSetDropSubAreaIds:
    def _patch(
        self,
        monkeypatch: pytest.MonkeyPatch,
        monsters_by_id: dict[int, SimpleNamespace],
        best_set: object,
        missing_gids: list[int],
    ) -> None:
        set_drop._sub_area_ids_by_drop_gid.cache_clear()
        monkeypatch.setattr(set_drop, "DataReader", _reader(monsters_by_id=monsters_by_id))
        monkeypatch.setattr(set_drop, "get_current_best_set", _const(best_set))
        monkeypatch.setattr(
            set_drop,
            "get_item_gids_to_buy",
            _const([SimpleNamespace(item_gid=gid) for gid in missing_gids]),
        )

    def test_returns_sub_areas_of_missing_pieces(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        self._patch(
            monkeypatch,
            {1: _monster([100], [11]), 2: _monster([200], [22])},
            best_set=object(),
            missing_gids=[100],
        )
        result = get_missing_set_drop_sub_area_ids(
            EffectElement.CHANCE, 50, True, _owned({})
        )
        assert result == frozenset({11})

    def test_empty_when_piece_already_owned(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        self._patch(
            monkeypatch,
            {1: _monster([100], [11])},
            best_set=object(),
            missing_gids=[100],
        )
        result = get_missing_set_drop_sub_area_ids(
            EffectElement.CHANCE, 50, True, _owned({1: 100})
        )
        assert result == frozenset()

    def test_empty_when_no_set(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self._patch(
            monkeypatch,
            {1: _monster([100], [11])},
            best_set=None,
            missing_gids=[100],
        )
        result = get_missing_set_drop_sub_area_ids(
            EffectElement.CHANCE, 50, True, _owned({})
        )
        assert result == frozenset()


class TestChooseSetDropSubAreaId:
    def _patch_sub_areas(
        self, monkeypatch: pytest.MonkeyPatch, level_by_id: dict[int, int]
    ) -> None:
        sub_area_by_id = {
            sub_area_id: SimpleNamespace(level=level, areaId=1)
            for sub_area_id, level in level_by_id.items()
        }
        monkeypatch.setattr(
            set_drop, "DataReader", _reader(sub_area_by_id=sub_area_by_id)
        )

    def test_picks_highest_reachable_level(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        self._patch_sub_areas(monkeypatch, {11: 10, 33: 18})
        assert choose_set_drop_sub_area_id(frozenset({11, 33}), 20, []) == 33

    def test_excludes_over_level_sub_areas(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        self._patch_sub_areas(monkeypatch, {11: 10, 22: 50})
        assert choose_set_drop_sub_area_id(frozenset({11, 22}), 20, []) == 11

    def test_none_when_nothing_reachable(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        self._patch_sub_areas(monkeypatch, {22: 50})
        assert choose_set_drop_sub_area_id(frozenset({22}), 5, []) is None
