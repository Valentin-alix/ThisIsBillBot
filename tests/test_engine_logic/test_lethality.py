from types import SimpleNamespace
from typing import cast
from unittest.mock import MagicMock

import msgspec
import pytest
from DBDofusUnity.dofus_unity_reader.game_constants.characteristic import EffectElement
from DBDofusUnity.dofus_unity_reader.grid.map_point import MapPoint
from DBDofusUnity.dofus_unity_reader.models.datas.spell_levels_root import Effect, SpellLevelsRootItem

from src.core.engine.contexts import AttackContext
from src.core.engine.fights.attack import lethality as lethality_module
from src.core.engine.fights.attack.enemy_data import EnemyData
from src.core.engine.fights.attack.lethality import can_finish_fight_this_turn
from src.core.engine.fights.damage_calculator import DamageCalculator
from tests.fixtures.data import make_spell_effect, make_spell_level


def _context(*, enemies_data: list[EnemyData], action_points: int = 6) -> AttackContext:
    return cast(
        AttackContext,
        SimpleNamespace(
            enemies_data=enemies_data,
            action_points=action_points,
            player_map_point=MapPoint.from_cell_id(100),
            spells=[],
            primary_elem=0,
            characteristic_by_id={},
            modifier_by_type_and_spell_id={},
            range=0,
        ),
    )


def _enemy(life_point: int) -> EnemyData:
    return EnemyData(
        actor=MagicMock(),
        map_point=MapPoint.from_cell_id(200),
        life_point=life_point,
        max_life_point=max(life_point, 1),
        is_summoned=False,
        monster_grade=MagicMock(),
        movement_points=0,
        max_spell_range=0,
    )


def _damage_calculator(damage_per_cast: int) -> DamageCalculator:
    calculator = MagicMock(spec=DamageCalculator)
    calculator.get_damage_effect.return_value = damage_per_cast
    return calculator


def _patch_single_damage_spell(monkeypatch: pytest.MonkeyPatch, *, ap_cost: int = 3) -> None:
    spell_lvl = msgspec.structs.replace(make_spell_level(), apCost=ap_cost)
    effect = make_spell_effect(effect_id=1, effect_element=EffectElement.NEUTRAL_ELEMENT)

    def _fake(*_args: object, **_kwargs: object) -> list[tuple[SpellLevelsRootItem, Effect]]:
        return [(spell_lvl, effect)]

    monkeypatch.setattr(lethality_module, "get_damage_spells", _fake)


class TestCanFinishFightThisTurn:
    def test_true_with_no_enemies(self) -> None:
        assert can_finish_fight_this_turn(_context(enemies_data=[]), MagicMock()) is True

    def test_false_with_multiple_enemies(self) -> None:
        context = _context(enemies_data=[_enemy(10), _enemy(10)])
        assert can_finish_fight_this_turn(context, MagicMock()) is False

    def test_true_when_last_enemy_already_dead(self) -> None:
        context = _context(enemies_data=[_enemy(0)])
        assert can_finish_fight_this_turn(context, MagicMock()) is True

    def test_true_when_estimated_damage_covers_remaining_life(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _patch_single_damage_spell(monkeypatch, ap_cost=3)
        context = _context(enemies_data=[_enemy(50)], action_points=6)
        assert can_finish_fight_this_turn(context, _damage_calculator(30)) is True

    def test_false_when_enemy_is_too_tanky(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _patch_single_damage_spell(monkeypatch, ap_cost=3)
        context = _context(enemies_data=[_enemy(5000)], action_points=6)
        assert can_finish_fight_this_turn(context, _damage_calculator(30)) is False
