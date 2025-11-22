from types import SimpleNamespace
from typing import cast

import msgspec
import pytest

from src.core.engine.contexts import AttackContext
from src.core.engine.fights.attack import spell_filter as spell_filter_module
from tests.fixtures.data import make_spell_level


class TestResolveCastableSpellLvl:
    def test_none_when_spell_not_known(self) -> None:
        context = cast(AttackContext, SimpleNamespace(spells=[]))
        assert spell_filter_module.resolve_castable_spell_lvl(context, 12737) is None

    def test_returns_spell_lvl_when_valid_for_turn(self, monkeypatch: pytest.MonkeyPatch) -> None:
        spell_lvl = msgspec.structs.replace(make_spell_level(), spellId=12737)
        spell_item = SimpleNamespace(spell_id=12737, spell_level=1)
        context = cast(
            AttackContext,
            SimpleNamespace(spells=[spell_item], range=0, modifier_by_type_and_spell_id={}),
        )
        monkeypatch.setattr(
            spell_filter_module,
            "DataReader",
            lambda: SimpleNamespace(spell_lvl_by_spell_id={12737: [spell_lvl]}),
        )
        monkeypatch.setattr(spell_filter_module, "is_spell_valid_for_turn", _always_valid_for_turn)
        assert spell_filter_module.resolve_castable_spell_lvl(context, 12737) is spell_lvl

    def test_none_when_not_valid_for_turn(self, monkeypatch: pytest.MonkeyPatch) -> None:
        spell_lvl = msgspec.structs.replace(make_spell_level(), spellId=12737)
        spell_item = SimpleNamespace(spell_id=12737, spell_level=1)
        context = cast(
            AttackContext,
            SimpleNamespace(spells=[spell_item], range=0, modifier_by_type_and_spell_id={}),
        )
        monkeypatch.setattr(
            spell_filter_module,
            "DataReader",
            lambda: SimpleNamespace(spell_lvl_by_spell_id={12737: [spell_lvl]}),
        )
        monkeypatch.setattr(spell_filter_module, "is_spell_valid_for_turn", _never_valid_for_turn)
        assert spell_filter_module.resolve_castable_spell_lvl(context, 12737) is None


def _always_valid_for_turn(*_args: object) -> bool:
    return True


def _never_valid_for_turn(*_args: object) -> bool:
    return False
