from types import SimpleNamespace
from typing import cast
from unittest.mock import MagicMock

import msgspec
import pytest
from DBDofusUnity.dofus_unity_reader.game_constants.characteristic import EffectElement
from DBDofusUnity.dofus_unity_reader.models.datas.spell_levels_root import (
    Effect,
    SpellLevelsRootItem,
)

from src.core.engine.contexts import AttackContext
from src.core.engine.fights import effect as effect_module
from src.core.engine.fights.attack import buff
from src.core.engine.fights.attack.buff import find_best_self_buff
from src.core.engine.fights.effect import (
    is_offensive_self_buff_effect,
    is_self_shield_effect,
)
from src.core.engine.fights.spell_modifier import SpellModifiers
from tests.fixtures.data import make_spell_effect, make_spell_level


def _effect() -> Effect:
    return make_spell_effect(effect_id=1, effect_element=EffectElement.STRENGTH)


def _spell(spell_id: int) -> SpellLevelsRootItem:
    return msgspec.structs.replace(make_spell_level(), spellId=spell_id)


def _modifiers(ap_cost: int) -> SpellModifiers:
    return cast(SpellModifiers, SimpleNamespace(ap_cost=ap_cost))


class TestIsOffensiveSelfBuffEffect:
    def _patch(self, monkeypatch: pytest.MonkeyPatch, description_id: int) -> None:
        monkeypatch.setattr(
            effect_module,
            "DataReader",
            lambda: SimpleNamespace(effect_by_id={1: SimpleNamespace(descriptionId=description_id)}),
        )

    def test_detects_buff(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self._patch(monkeypatch, next(iter(effect_module.OFFENSIVE_SELF_BUFF_DESCRIPTION_IDS)))
        assert is_offensive_self_buff_effect(_effect()) is True

    def test_rejects_non_buff(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self._patch(monkeypatch, 999999)
        assert is_offensive_self_buff_effect(_effect()) is False

    def test_detects_shield(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self._patch(monkeypatch, next(iter(effect_module.SHIELD_DESCRIPTION_IDS)))
        assert is_self_shield_effect(_effect()) is True

    def test_rejects_non_shield(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self._patch(monkeypatch, 999999)
        assert is_self_shield_effect(_effect()) is False


class TestFindBestSelfBuff:
    def _patch_candidates(
        self,
        monkeypatch: pytest.MonkeyPatch,
        candidates: list[tuple[SpellLevelsRootItem, Effect, SpellModifiers]],
    ) -> None:
        def _fake(
            _context: AttackContext,
        ) -> list[tuple[SpellLevelsRootItem, Effect, SpellModifiers]]:
            return candidates

        monkeypatch.setattr(buff, "get_valid_self_buff_spells_for_turn", _fake)

    def test_none_when_no_candidates(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self._patch_candidates(monkeypatch, [])
        assert find_best_self_buff(cast(AttackContext, SimpleNamespace()), MagicMock()) is None

    def test_picks_cheapest_buff(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self._patch_candidates(
            monkeypatch,
            [
                (_spell(10), _effect(), _modifiers(3)),
                (_spell(20), _effect(), _modifiers(1)),
                (_spell(30), _effect(), _modifiers(2)),
            ],
        )
        best = find_best_self_buff(cast(AttackContext, SimpleNamespace()), MagicMock())
        assert best is not None
        assert best.spellId == 20
