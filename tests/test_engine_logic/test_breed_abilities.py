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
    return BreedAbilitySelector(
        _logger=MagicMock(), fight_reachable_cells=MagicMock(), damage_calculator=MagicMock()
    )


def _context(breed_id: int) -> AttackContext:
    return cast(AttackContext, SimpleNamespace(breed_id=breed_id))


@pytest.mark.parametrize("urgent", [False, True], ids=["normal", "urgent"])
class TestFindSupportAction:
    def test_returns_first_rule_that_fires(self, monkeypatch: pytest.MonkeyPatch, urgent: bool) -> None:
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
            breed_abilities_module._BREED_URGENT_RULES if urgent else breed_abilities_module._BREED_RULES,
            BreedEnum.SACRIER,
            [_rule_none, _rule_hit, _fail_if_called],
        )

        context = _context(breed_id=BreedEnum.SACRIER)
        selector = _make_selector()
        find_action = selector.find_urgent_support_action if urgent else selector.find_support_action
        assert find_action(context) == expected

    def test_none_when_no_rule_fires(self, monkeypatch: pytest.MonkeyPatch, urgent: bool) -> None:
        def _rule_none(
            _context: AttackContext, _cells: FightReachableCells, _damage_calculator: DamageCalculator
        ) -> SupportAction | None:
            return None

        monkeypatch.setitem(
            breed_abilities_module._BREED_URGENT_RULES if urgent else breed_abilities_module._BREED_RULES,
            BreedEnum.SACRIER,
            [_rule_none],
        )

        context = _context(breed_id=BreedEnum.SACRIER)
        selector = _make_selector()
        find_action = selector.find_urgent_support_action if urgent else selector.find_support_action
        assert find_action(context) is None
