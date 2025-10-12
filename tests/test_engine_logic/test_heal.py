from types import SimpleNamespace
from typing import cast
from unittest.mock import MagicMock

import msgspec
import pytest
from DBDofusUnity.dofus_unity_reader.game_constants.characteristic import (
    CharacteristicEnum,
    EffectElement,
)
from DBDofusUnity.dofus_unity_reader.game_constants.description import DescriptionEnum
from DBDofusUnity.dofus_unity_reader.models.datas.spell_levels_root import (
    Effect,
    SpellLevelsRootItem,
)

from src.core.engine.contexts import AttackContext
from src.core.engine.fights import effect as effect_module
from src.core.engine.fights.attack import heal
from src.core.engine.fights.attack.heal import (
    estimate_self_heal,
    find_best_self_heal,
    is_heal_effect,
)
from src.core.engine.fights.effect import can_self_cast
from src.core.engine.fights.spell_modifier import SpellModifiers
from tests.fixtures.data import (
    make_characteristics,
    make_spell_effect,
    make_spell_level,
)


def _effect(
    *,
    target_mask: str = "C",
    dice_num: int = 0,
    dice_side: int = 0,
    value: int = 0,
) -> Effect:
    return msgspec.structs.replace(
        make_spell_effect(effect_id=1, effect_element=EffectElement.INTELLIGENCE),
        targetMask=target_mask,
        diceNum=dice_num,
        diceSide=dice_side,
        value=value,
    )


def _spell(spell_id: int) -> SpellLevelsRootItem:
    return msgspec.structs.replace(make_spell_level(), spellId=spell_id)


def _modifiers(ap_cost: int) -> SpellModifiers:
    return cast(SpellModifiers, SimpleNamespace(ap_cost=ap_cost))


def _context(
    *,
    life_point: int = 300,
    max_life_point: int = 1000,
) -> AttackContext:
    return cast(
        AttackContext,
        SimpleNamespace(
            life_point=life_point,
            max_life_point=max_life_point,
            life_percentage=life_point / max_life_point,
            characteristic_by_id={},
        ),
    )


class TestIsHealEffect:
    def _patch_description_id(self, monkeypatch: pytest.MonkeyPatch, description_id: int) -> None:
        monkeypatch.setattr(
            effect_module,
            "DataReader",
            lambda: SimpleNamespace(effect_by_id={1: SimpleNamespace(descriptionId=description_id)}),
        )

    def test_detects_heal_description_id(self, monkeypatch: pytest.MonkeyPatch) -> None:
        heal_description_id = next(iter(effect_module.HEAL_DESCRIPTION_IDS))
        self._patch_description_id(monkeypatch, heal_description_id)
        assert is_heal_effect(_effect()) is True

    def test_rejects_non_heal_description_id(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self._patch_description_id(monkeypatch, 999999)
        assert is_heal_effect(_effect()) is False


class TestCanSelfCast:
    def test_self_mask_is_castable(self) -> None:
        assert can_self_cast(_effect(target_mask="C")) is True
        assert can_self_cast(_effect(target_mask="a")) is True

    def test_enemy_only_mask_is_not_castable(self) -> None:
        assert can_self_cast(_effect(target_mask="A")) is False


def _patch_effect_description(monkeypatch: pytest.MonkeyPatch, description_id: int) -> None:
    monkeypatch.setattr(
        heal,
        "DataReader",
        lambda: SimpleNamespace(effect_by_id={1: SimpleNamespace(descriptionId=description_id)}),
    )


class TestEstimateSelfHeal:
    def test_elemental_heal_scales_with_intelligence(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _patch_effect_description(monkeypatch, 0)
        context = cast(
            AttackContext,
            SimpleNamespace(
                characteristic_by_id=make_characteristics(
                    {
                        CharacteristicEnum.INTELLIGENCE: 100,
                        CharacteristicEnum.HEAL_BONUS: 10,
                    }
                )
            ),
        )

        heal_amount = estimate_self_heal(_effect(dice_num=40, dice_side=60), context)
        assert heal_amount == 110

    def test_percent_max_life_heal(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _patch_effect_description(monkeypatch, DescriptionEnum.HEAL_PERCENT_MAX_LIFE)
        context = cast(
            AttackContext,
            SimpleNamespace(max_life_point=1000, characteristic_by_id={}),
        )

        assert estimate_self_heal(_effect(dice_num=30, dice_side=30), context) == 300

    def test_flat_heal_has_no_stat_scaling(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _patch_effect_description(monkeypatch, DescriptionEnum.HEAL_FLAT_LIFE)
        context = cast(
            AttackContext,
            SimpleNamespace(
                characteristic_by_id=make_characteristics({CharacteristicEnum.INTELLIGENCE: 100})
            ),
        )

        assert estimate_self_heal(_effect(dice_num=50, dice_side=50), context) == 50


class TestFindBestSelfHeal:
    def _patch_spells(
        self,
        monkeypatch: pytest.MonkeyPatch,
        spells: list[tuple[SpellLevelsRootItem, Effect, SpellModifiers]],
    ) -> None:
        _patch_effect_description(monkeypatch, 0)

        def _fake(
            _context: AttackContext,
        ) -> list[tuple[SpellLevelsRootItem, Effect, SpellModifiers]]:
            return spells

        monkeypatch.setattr(heal, "get_valid_heal_spells_for_turn", _fake)

    def test_no_heal_when_no_spells(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self._patch_spells(monkeypatch, [])
        assert find_best_self_heal(_context(life_point=100), MagicMock()) is None

    def test_picks_most_efficient_heal(self, monkeypatch: pytest.MonkeyPatch) -> None:

        self._patch_spells(
            monkeypatch,
            [
                (_spell(1), _effect(dice_num=300, dice_side=300), _modifiers(3)),
                (_spell(2), _effect(dice_num=300, dice_side=300), _modifiers(2)),
            ],
        )
        best = find_best_self_heal(_context(life_point=300), MagicMock())
        assert best is not None
        assert best.spellId == 2
