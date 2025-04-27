from types import SimpleNamespace
from typing import cast

import pytest
from datas.protos.non_obf.game.common_pb2 import ObjectItemInventory
from dofus_unity_reader.game_constants.characteristic import (
    CharacteristicEnum,
    EffectElement,
)

from src.core.engine.items import equipment
from src.core.engine.items.equipment import get_best_roll, roll_score

# Arbitrary effect (action) ids mapped to the characteristic they grant.
_WATER_DMG_ACTION = 1
_VITALITY_ACTION = 2
_CHANCE_ACTION = 3
_EFFECT_BY_ID = {
    _WATER_DMG_ACTION: SimpleNamespace(
        characteristic=CharacteristicEnum.WATER_DAMAGE_BONUS
    ),
    _VITALITY_ACTION: SimpleNamespace(characteristic=CharacteristicEnum.VITALITY),
    _CHANCE_ACTION: SimpleNamespace(characteristic=CharacteristicEnum.CHANCE),
}


def _patch_effects(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        equipment,
        "DataReader",
        lambda: SimpleNamespace(effect_by_id=_EFFECT_BY_ID),
    )


def _item(effects: list[tuple[int, int]]) -> ObjectItemInventory:
    return cast(
        ObjectItemInventory,
        SimpleNamespace(
            item=SimpleNamespace(
                gid=1,
                effects=[
                    SimpleNamespace(action=action, value_int=value)
                    for action, value in effects
                ],
            )
        ),
    )


class TestRollScore:
    # Build is Chance -> primary element Water.
    PRIMARY = EffectElement.CHANCE

    def test_water_damage_weighted_above_vitality(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _patch_effects(monkeypatch)
        water = _item([(_WATER_DMG_ACTION, 10)])
        vitality = _item([(_VITALITY_ACTION, 10)])
        assert roll_score(water, self.PRIMARY) > roll_score(vitality, self.PRIMARY)

    def test_primary_stat_weighted_above_vitality(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _patch_effects(monkeypatch)
        chance = _item([(_CHANCE_ACTION, 10)])
        vitality = _item([(_VITALITY_ACTION, 10)])
        assert roll_score(chance, self.PRIMARY) > roll_score(vitality, self.PRIMARY)

    def test_best_roll_prefers_better_damage_roll(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _patch_effects(monkeypatch)
        better_damage = _item([(_WATER_DMG_ACTION, 10), (_VITALITY_ACTION, 10)])
        better_vitality = _item([(_WATER_DMG_ACTION, 5), (_VITALITY_ACTION, 15)])
        best = get_best_roll([better_vitality, better_damage], self.PRIMARY)
        assert best is better_damage

    def test_unknown_effect_uses_default_weight(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _patch_effects(monkeypatch)
        unknown = _item([(999, 10)])
        assert roll_score(unknown, self.PRIMARY) == 5.0
