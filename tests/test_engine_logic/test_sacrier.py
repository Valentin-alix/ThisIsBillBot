from types import SimpleNamespace
from typing import cast
from unittest.mock import MagicMock

import msgspec
import pytest
from DBDofusUnity.dofus_unity_reader.models.datas.spell_levels_root import SpellLevelsRootItem

from DBDofusUnity.dofus_unity_reader.grid.map_point import MapPoint

from src.core.engine.contexts import AttackContext
from src.core.engine.fights.attack.breed import sacrier as sacrier_module
from src.core.engine.fights.attack.positions import AttackPositions
from src.core.engine.fights.reachable_cells.fight_reachable_cells import FightReachableCells
from tests.fixtures.data import make_spell_level


class FakeMapPoint:
    """Stands in for MapPoint in unit tests: no `__lt__`, like the real thing."""

    def __init__(self, name: str, dist: float = 0) -> None:
        self.cell_id = name
        self._dist = dist

    def distance_to_map_point(self, _other: object) -> float:
        return self._dist

    def __repr__(self) -> str:
        return f"FakeMapPoint({self.cell_id})"


def _context(
    *,
    enemies_data: list[object] | None = None,
    cast_turn_by_spell_id: dict[int, int] | None = None,
    life_percentage: float = 1.0,
    player_map_point: object = "player_mp",
    range_: int = 0,
    own_active_summon_count: int = 0,
    max_active_summon_count: int = 1,
) -> AttackContext:
    return cast(
        AttackContext,
        SimpleNamespace(
            enemies_data=enemies_data if enemies_data is not None else ["enemy"],
            cast_turn_by_spell_id=cast_turn_by_spell_id if cast_turn_by_spell_id is not None else {},
            life_percentage=life_percentage,
            player_map_point=player_map_point,
            range=range_,
            modifier_by_type_and_spell_id={},
            own_active_summon_count=own_active_summon_count,
            max_active_summon_count=max_active_summon_count,
        ),
    )


def _fight_could_finish_this_turn(_context: AttackContext, _damage_calculator: object) -> bool:
    return True


class TestFindMutilationInitialCast:
    def test_none_when_fight_could_finish_this_turn(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(sacrier_module, "can_finish_fight_this_turn", _fight_could_finish_this_turn)
        context = _context(enemies_data=["enemy"], life_percentage=1.0)
        assert sacrier_module._find_mutilation_initial_cast(context, MagicMock(), MagicMock()) is None

    def test_none_when_life_at_or_below_threshold(self) -> None:
        context = _context(
            enemies_data=["enemy1", "enemy2"],
            life_percentage=sacrier_module.MUTILATION_RECAST_LIFE_THRESHOLD,
        )
        assert sacrier_module._find_mutilation_initial_cast(context, MagicMock(), MagicMock()) is None

    def test_none_when_already_cast_this_fight(self) -> None:
        context = _context(
            enemies_data=["enemy1", "enemy2"],
            cast_turn_by_spell_id={sacrier_module.SACRIER_MUTILATION_SPELL_ID: 1},
            life_percentage=1.0,
        )
        assert sacrier_module._find_mutilation_initial_cast(context, MagicMock(), MagicMock()) is None

    def test_returns_self_cast_when_conditions_met(self, monkeypatch: pytest.MonkeyPatch) -> None:
        spell_lvl = msgspec.structs.replace(make_spell_level(), spellId=sacrier_module.SACRIER_MUTILATION_SPELL_ID)

        def _resolve(_context: AttackContext, _spell_id: int) -> SpellLevelsRootItem | None:
            return spell_lvl

        monkeypatch.setattr(sacrier_module, "resolve_castable_spell_lvl", _resolve)
        context = _context(enemies_data=["enemy1", "enemy2"], life_percentage=1.0)
        result = sacrier_module._find_mutilation_initial_cast(context, MagicMock(), MagicMock())
        assert result == (context.player_map_point, spell_lvl, context.player_map_point)


class TestFindMutilationRecast:
    def test_none_when_fight_could_finish_this_turn(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(sacrier_module, "can_finish_fight_this_turn", _fight_could_finish_this_turn)
        context = _context(
            enemies_data=["enemy"],
            cast_turn_by_spell_id={sacrier_module.SACRIER_MUTILATION_SPELL_ID: 1},
            life_percentage=0.1,
        )
        assert sacrier_module._find_mutilation_recast(context, MagicMock(), MagicMock()) is None

    def test_none_when_not_cast_yet_this_fight(self) -> None:
        context = _context(enemies_data=["enemy1", "enemy2"], life_percentage=0.1)
        assert sacrier_module._find_mutilation_recast(context, MagicMock(), MagicMock()) is None

    def test_none_when_life_above_threshold(self) -> None:
        context = _context(
            enemies_data=["enemy1", "enemy2"],
            cast_turn_by_spell_id={sacrier_module.SACRIER_MUTILATION_SPELL_ID: 1},
            life_percentage=sacrier_module.MUTILATION_RECAST_LIFE_THRESHOLD + 0.01,
        )
        assert sacrier_module._find_mutilation_recast(context, MagicMock(), MagicMock()) is None

    def test_returns_self_cast_when_conditions_met(self, monkeypatch: pytest.MonkeyPatch) -> None:
        spell_lvl = msgspec.structs.replace(make_spell_level(), spellId=sacrier_module.SACRIER_MUTILATION_SPELL_ID)

        def _resolve(_context: AttackContext, _spell_id: int) -> SpellLevelsRootItem | None:
            return spell_lvl

        monkeypatch.setattr(sacrier_module, "resolve_castable_spell_lvl", _resolve)
        context = _context(
            enemies_data=["enemy1", "enemy2"],
            cast_turn_by_spell_id={sacrier_module.SACRIER_MUTILATION_SPELL_ID: 1},
            life_percentage=sacrier_module.MUTILATION_RECAST_LIFE_THRESHOLD,
        )
        result = sacrier_module._find_mutilation_recast(context, MagicMock(), MagicMock())
        assert result == (context.player_map_point, spell_lvl, context.player_map_point)


class TestFindInvocation:
    def test_none_when_fight_could_finish_this_turn(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(sacrier_module, "can_finish_fight_this_turn", _fight_could_finish_this_turn)
        context = _context(enemies_data=["enemy"])
        assert sacrier_module._find_invocation(context, MagicMock(), MagicMock()) is None

    def test_none_when_at_max_active_summons(self) -> None:
        context = _context(
            enemies_data=["enemy1", "enemy2"], own_active_summon_count=1, max_active_summon_count=1
        )
        assert sacrier_module._find_invocation(context, MagicMock(), MagicMock()) is None

    def test_none_when_spell_not_castable(self, monkeypatch: pytest.MonkeyPatch) -> None:
        def _resolve(_context: AttackContext, _spell_id: int) -> SpellLevelsRootItem | None:
            return None

        monkeypatch.setattr(sacrier_module, "resolve_castable_spell_lvl", _resolve)
        context = _context(enemies_data=["enemy1", "enemy2"])
        assert sacrier_module._find_invocation(context, MagicMock(), MagicMock()) is None

    def test_no_crash_and_picks_a_cell_when_candidates_tie(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Regression test: candidates tying on (distance, remaining_pm) used to crash
        comparing MapPoint objects (no `__lt__`) as the tuple tie-breaker."""
        spell_lvl = msgspec.structs.replace(make_spell_level(), spellId=sacrier_module.SACRIER_EPEE_VORACE_SPELL_ID)

        def _resolve(_context: AttackContext, _spell_id: int) -> SpellLevelsRootItem | None:
            return spell_lvl

        movable_mp_a = cast(MapPoint, FakeMapPoint("movable_a"))
        movable_mp_b = cast(MapPoint, FakeMapPoint("movable_b"))
        target_mp_a = cast(MapPoint, FakeMapPoint("target_a", dist=5))
        target_mp_b = cast(MapPoint, FakeMapPoint("target_b", dist=5))
        enemy_mp = cast(MapPoint, FakeMapPoint("enemy"))

        positions = AttackPositions(entities_mp=set(), entities_id_by_mp={}, enemies_mp={enemy_mp})

        def _get_positions(_context: AttackContext) -> AttackPositions:
            return positions

        def _get_movable_mps(
            _context: AttackContext, _positions: AttackPositions, _cells: FightReachableCells
        ) -> dict[MapPoint, int]:
            return {movable_mp_a: 2, movable_mp_b: 2}

        def _fake_possible_mps(movable_mp: MapPoint, *_args: object, **_kwargs: object) -> set[MapPoint]:
            return {target_mp_a} if movable_mp is movable_mp_a else {target_mp_b}

        def _always_castable(*_args: object, **_kwargs: object) -> bool:
            return True

        monkeypatch.setattr(sacrier_module, "resolve_castable_spell_lvl", _resolve)
        monkeypatch.setattr(sacrier_module, "get_positions", _get_positions)
        monkeypatch.setattr(sacrier_module, "get_movable_mps", _get_movable_mps)
        monkeypatch.setattr(sacrier_module, "get_possible_mp_spell", _fake_possible_mps)
        monkeypatch.setattr(sacrier_module, "can_cast_spell_on_mp", _always_castable)

        context = _context(enemies_data=["enemy1", "enemy2"])
        result = sacrier_module._find_invocation(context, MagicMock(), MagicMock())

        assert result is not None
        move_mp, returned_spell_lvl, target_mp = result
        assert returned_spell_lvl is spell_lvl
        assert move_mp in (movable_mp_a, movable_mp_b)
        assert target_mp in (target_mp_a, target_mp_b)


class TestSacrierRules:
    def test_rules_and_urgent_rules_split(self) -> None:
        assert sacrier_module.RULES == [sacrier_module._find_invocation]
        assert sacrier_module.URGENT_RULES == [
            sacrier_module._find_mutilation_initial_cast,
            sacrier_module._find_mutilation_recast,
        ]
