from types import SimpleNamespace
from typing import cast

import pytest
from dofus_unity_reader.grid.map_point import MapPoint

from src.core.engine.fights.attack import push
from src.core.engine.fights.attack.push import estimate_collision_damage


def _mp(x: int, y: int, cell_id: int) -> MapPoint:
    return cast(MapPoint, SimpleNamespace(x=x, y=y, cell_id=cell_id))


def _patch_grid(
    monkeypatch: pytest.MonkeyPatch,
    coord_to_mp: dict[tuple[int, int], MapPoint],
    blocked_cell_ids: set[int],
) -> None:
    monkeypatch.setattr(push, "MAP_POINT_BY_COORD", coord_to_mp)

    def _get_cell(_map_id: int, cell_id: int) -> SimpleNamespace:
        return SimpleNamespace(mov=cell_id not in blocked_cell_ids, nonWalkableDuringFight=0)

    monkeypatch.setattr(
        push,
        "MapReader",
        lambda: SimpleNamespace(get_cell_data_by_cell_id=_get_cell),
    )


_CASTER = _mp(0, 0, 0)
_ENEMY = _mp(1, 0, 1)


class TestEstimateCollisionDamage:
    def test_free_push_deals_no_damage(self, monkeypatch: pytest.MonkeyPatch) -> None:
        grid = {(2, 0): _mp(2, 0, 2), (3, 0): _mp(3, 0, 3), (4, 0): _mp(4, 0, 4)}
        _patch_grid(monkeypatch, grid, set())
        assert estimate_collision_damage(_CASTER, _ENEMY, 3, 0, set(), 200, 0) == 0

    def test_wall_collision(self, monkeypatch: pytest.MonkeyPatch) -> None:
        grid = {(2, 0): _mp(2, 0, 2), (3, 0): _mp(3, 0, 3), (4, 0): _mp(4, 0, 4)}
        _patch_grid(monkeypatch, grid, {3})

        assert estimate_collision_damage(_CASTER, _ENEMY, 3, 0, set(), 200, 0) == 66

    def test_fighter_collision(self, monkeypatch: pytest.MonkeyPatch) -> None:
        grid = {(2, 0): _mp(2, 0, 2), (3, 0): _mp(3, 0, 3)}
        _patch_grid(monkeypatch, grid, set())
        assert estimate_collision_damage(_CASTER, _ENEMY, 3, 0, {3}, 200, 0) == 66

    def test_map_edge_blocks(self, monkeypatch: pytest.MonkeyPatch) -> None:
        grid = {(2, 0): _mp(2, 0, 2)}
        _patch_grid(monkeypatch, grid, set())
        assert estimate_collision_damage(_CASTER, _ENEMY, 3, 0, set(), 200, 0) == 66

    def test_push_damage_bonus_increases_damage(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _patch_grid(monkeypatch, {}, set())

        assert estimate_collision_damage(_CASTER, _ENEMY, 3, 0, set(), 200, 20) == 114

    def test_no_direction_returns_zero(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _patch_grid(monkeypatch, {}, set())
        same = _mp(1, 1, 1)
        assert estimate_collision_damage(same, same, 3, 0, set(), 200, 0) == 0
