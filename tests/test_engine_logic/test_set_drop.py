from types import SimpleNamespace
from typing import Callable, cast

import pytest
from datas.protos.non_obf.game.common_pb2 import ObjectItemInventory
from dofus_unity_reader.data_center.area_info import AreaInfo
from dofus_unity_reader.game_constants.characteristic import EffectElement

from src.core.engine.weights.fighter import set_drop
from src.core.engine.weights.fighter.set_drop import (
    choose_set_drop_area_info,
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


def _sub_area(dungeon_id: int = 0, on_world_map: int = 1) -> SimpleNamespace:
    return SimpleNamespace(dungeonId=dungeon_id, displayOnWorldMap=on_world_map)


class TestChooseSetDropAreaInfo:
    # Curated candidates: an area-level one (area 1 covers sub-areas 11/12),
    # a curated sub-area one (sub-area 22), and a high-level area (area 3).
    AREA_LEVEL = AreaInfo(area_id=1, min_lvl=1)
    SUB_AREA_LEVEL = AreaInfo(area_id=2, sub_area_id=22, min_lvl=1)
    HIGH_LEVEL = AreaInfo(area_id=3, min_lvl=50)

    def _patch(
        self,
        monkeypatch: pytest.MonkeyPatch,
        sub_area_by_id: dict[int, SimpleNamespace] | None = None,
    ) -> None:
        candidates = [self.AREA_LEVEL, self.SUB_AREA_LEVEL, self.HIGH_LEVEL]
        monkeypatch.setattr(set_drop, "AREAS_SUB_WITH_WEIGHT", candidates)
        monkeypatch.setattr(set_drop, "AREAS_UNSUB_WITH_WEIGHT", candidates)
        monkeypatch.setattr(
            set_drop,
            "DataReader",
            _reader(
                sub_areas_by_area_id={1: {11, 12}, 2: {22}, 3: {33}},
                sub_area_by_id=sub_area_by_id
                or {
                    11: _sub_area(),
                    12: _sub_area(),
                    22: _sub_area(),
                    33: _sub_area(),
                },
            ),
        )

    def test_narrows_area_level_candidate_to_drop_sub_area(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        self._patch(monkeypatch)
        # area-level candidate (area 1) narrows to the covered drop sub-area 11.
        assert choose_set_drop_area_info(
            frozenset({11}), 20, True, frozenset(), []
        ) == AreaInfo(area_id=1, sub_area_id=11, min_lvl=1)

    def test_matches_curated_sub_area_candidate(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        self._patch(monkeypatch)
        assert (
            choose_set_drop_area_info(frozenset({22}), 20, True, frozenset(), [])
            == self.SUB_AREA_LEVEL
        )

    def test_skips_dungeon_drop_sub_area(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # sub-area 11 drops the piece but is a dungeon -> not reachable -> skipped.
        self._patch(
            monkeypatch,
            sub_area_by_id={11: _sub_area(dungeon_id=42), 12: _sub_area()},
        )
        assert (
            choose_set_drop_area_info(frozenset({11}), 20, True, frozenset(), []) is None
        )

    def test_excludes_over_level_candidate(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        self._patch(monkeypatch)
        # 33 only drops in the min_lvl=50 area -> unreachable for a level-20 player.
        assert (
            choose_set_drop_area_info(frozenset({33}), 20, True, frozenset(), []) is None
        )

    def test_none_when_no_candidate_covers(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        self._patch(monkeypatch)
        assert (
            choose_set_drop_area_info(frozenset({99}), 20, True, frozenset(), []) is None
        )

    def test_none_when_no_missing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self._patch(monkeypatch)
        assert (
            choose_set_drop_area_info(frozenset(), 20, True, frozenset(), []) is None
        )
