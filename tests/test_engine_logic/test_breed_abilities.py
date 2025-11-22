from types import SimpleNamespace
from typing import cast
from unittest.mock import MagicMock

import pytest
from DBDofusUnity.dofus_unity_reader.game_constants.breed import BreedEnum
from DBDofusUnity.dofus_unity_reader.grid.map_point import MapPoint
from DBDofusUnity.dofus_unity_reader.models.datas.spell_levels_root import SpellLevelsRootItem

from src.core.engine.contexts import AttackContext
from src.core.engine.fights.attack import breed_abilities as breed_abilities_module
from src.core.engine.fights.attack.breed.types import SupportAction
from src.core.engine.fights.attack.breed_abilities import BreedAbilitySelector
from src.core.engine.fights.damage_calculator import DamageCalculator
from src.core.engine.fights.reachable_cells.fight_reachable_cells import FightReachableCells


def _make_selector() -> BreedAbilitySelector:
    return BreedAbilitySelector(_logger=MagicMock(), fight_reachable_cells=MagicMock(), damage_calculator=MagicMock())


def _context(breed_id: int) -> AttackContext:
    return cast(AttackContext, SimpleNamespace(breed_id=breed_id))


class TestFindSupportAction:
    def test_none_for_breed_without_registered_rules(self) -> None:
        context = _context(breed_id=BreedEnum.CRA)
        assert _make_selector().find_support_action(context) is None

    def test_returns_first_rule_that_fires(self, monkeypatch: pytest.MonkeyPatch) -> None:
        expected: SupportAction = (
            cast(MapPoint, MagicMock()),
            cast(SpellLevelsRootItem, MagicMock()),
            cast(MapPoint, MagicMock()),
        )

        def _rule_none(
            _context: AttackContext, _cells: FightReachableCells, _damage_calculator: DamageCalculator
        ) -> SupportAction | None:
            return None

        def _rule_hit(
            _context: AttackContext, _cells: FightReachableCells, _damage_calculator: DamageCalculator
        ) -> SupportAction | None:
            return expected

        def _fail_if_called(
            _context: AttackContext, _cells: FightReachableCells, _damage_calculator: DamageCalculator
        ) -> SupportAction | None:
            raise AssertionError("rules after the first hit should not be tried")

        monkeypatch.setitem(
            breed_abilities_module._BREED_RULES,
            BreedEnum.SACRIER,
            [_rule_none, _rule_hit, _fail_if_called],
        )

        context = _context(breed_id=BreedEnum.SACRIER)
        assert _make_selector().find_support_action(context) == expected

    def test_none_when_no_rule_fires(self, monkeypatch: pytest.MonkeyPatch) -> None:
        def _rule_none(
            _context: AttackContext, _cells: FightReachableCells, _damage_calculator: DamageCalculator
        ) -> SupportAction | None:
            return None

        monkeypatch.setitem(breed_abilities_module._BREED_RULES, BreedEnum.SACRIER, [_rule_none])

        context = _context(breed_id=BreedEnum.SACRIER)
        assert _make_selector().find_support_action(context) is None


class TestFindUrgentSupportAction:
    def test_none_for_breed_without_registered_rules(self) -> None:
        context = _context(breed_id=BreedEnum.CRA)
        assert _make_selector().find_urgent_support_action(context) is None

    def test_returns_first_rule_that_fires(self, monkeypatch: pytest.MonkeyPatch) -> None:
        expected: SupportAction = (
            cast(MapPoint, MagicMock()),
            cast(SpellLevelsRootItem, MagicMock()),
            cast(MapPoint, MagicMock()),
        )

        def _rule_none(
            _context: AttackContext, _cells: FightReachableCells, _damage_calculator: DamageCalculator
        ) -> SupportAction | None:
            return None

        def _rule_hit(
            _context: AttackContext, _cells: FightReachableCells, _damage_calculator: DamageCalculator
        ) -> SupportAction | None:
            return expected

        monkeypatch.setitem(
            breed_abilities_module._BREED_URGENT_RULES,
            BreedEnum.SACRIER,
            [_rule_none, _rule_hit],
        )

        context = _context(breed_id=BreedEnum.SACRIER)
        assert _make_selector().find_urgent_support_action(context) == expected

    def test_none_when_no_rule_fires(self, monkeypatch: pytest.MonkeyPatch) -> None:
        def _rule_none(
            _context: AttackContext, _cells: FightReachableCells, _damage_calculator: DamageCalculator
        ) -> SupportAction | None:
            return None

        monkeypatch.setitem(breed_abilities_module._BREED_URGENT_RULES, BreedEnum.SACRIER, [_rule_none])

        context = _context(breed_id=BreedEnum.SACRIER)
        assert _make_selector().find_urgent_support_action(context) is None


class TestGetReservedAp:
    def test_zero_for_breed_without_registered_provider(self) -> None:
        context = _context(breed_id=BreedEnum.CRA)
        assert _make_selector().get_reserved_ap(context) == 0

    def test_delegates_to_registered_provider(self, monkeypatch: pytest.MonkeyPatch) -> None:
        def _provider(_context: AttackContext, _damage_calculator: DamageCalculator) -> int:
            return 3

        monkeypatch.setitem(breed_abilities_module._RESERVED_AP_PROVIDERS, BreedEnum.SACRIER, _provider)

        context = _context(breed_id=BreedEnum.SACRIER)
        assert _make_selector().get_reserved_ap(context) == 3
