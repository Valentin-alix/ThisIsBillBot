from types import SimpleNamespace
from typing import cast
from unittest.mock import MagicMock

import msgspec
import pytest
from DBDofusUnity.datas.protos.non_obf.game.common_pb2 import FightInvisibilityState
from DBDofusUnity.dofus_unity_reader.game_constants.characteristic import (
    EffectElement,
    TypeEffect,
)
from DBDofusUnity.dofus_unity_reader.grid.map_point import MapPoint
from DBDofusUnity.dofus_unity_reader.models.datas.spell_levels_root import (
    Effect,
    SpellLevelsRootItem,
)

from src.core.engine.contexts import AttackContext
from src.core.engine.fights import effect as effect_module
from src.core.engine.fights.attack import weight_calculator
from src.core.engine.fights.attack.enemy_data import EnemyData
from src.core.engine.fights.attack.weight_calculator import calculate_attack_weight
from src.core.engine.fights.spell_modifier import SpellModifiers
from tests.fixtures.data import make_spell_effect, make_spell_level, make_zone_descr


def _make_actor(*, actor_id: int, cell_id: int) -> object:
    return SimpleNamespace(actor_id=actor_id, disposition=SimpleNamespace(cell_id=cell_id))


def _make_context(
    *,
    life_point: int = 1000,
    max_life_point: int = 1000,
    player_level: int = 200,
    actor_by_id: dict[int, object] | None = None,
    enemy_actors: list[object] | None = None,
    invisible_enemy_cell_ids: frozenset[int] = frozenset(),
) -> AttackContext:
    return cast(
        AttackContext,
        SimpleNamespace(
            life_point=life_point,
            max_life_point=max_life_point,
            life_percentage=life_point / max_life_point,
            player_level=player_level,
            characteristic_by_id={},
            primary_elem=EffectElement.STRENGTH,
            player_map_point=MapPoint.from_cell_id(0),
            modifier_by_type_and_spell_id={},
            player_character_id=1,
            actor_by_id=actor_by_id or {},
            enemy_actors=enemy_actors or [],
            invisible_enemy_cell_ids=invisible_enemy_cell_ids,
        ),
    )


def _make_modifiers(ap_cost: int = 1) -> SpellModifiers:
    return cast(SpellModifiers, SimpleNamespace(ap_cost=ap_cost))


def _make_enemy(
    *,
    cell_id: int,
    life_point: int = 500,
    max_life_point: int = 500,
    is_summoned: bool = False,
    invisibility: FightInvisibilityState = FightInvisibilityState.VISIBLE,
    state_ids: frozenset[int] = frozenset(),
) -> EnemyData:
    return EnemyData(
        actor=MagicMock(),
        map_point=MapPoint.from_cell_id(cell_id),
        life_point=life_point,
        max_life_point=max_life_point,
        is_summoned=is_summoned,
        monster_grade=MagicMock(),
        movement_points=0,
        max_spell_range=0,
        invisibility=invisibility,
        state_ids=state_ids,
    )


def _make_effect(*, step_percent: int = 0, max_apply: int = 0) -> Effect:
    zone = msgspec.structs.replace(
        make_zone_descr(),
        damageDecreaseStepPercent=step_percent,
        maxDamageDecreaseApplyCount=max_apply,
    )
    return msgspec.structs.replace(
        make_spell_effect(effect_id=1, effect_element=EffectElement.STRENGTH),
        zoneDescr=zone,
        targetMask="A",
    )


def _stub_no_type_effect(monkeypatch: pytest.MonkeyPatch) -> None:
    def _no_type(spell_id: int, effect: Effect) -> TypeEffect | None:
        return None

    monkeypatch.setattr(weight_calculator, "get_type_effect", _no_type)


def _stub_malus_life_percent(monkeypatch: pytest.MonkeyPatch, malus: int) -> None:
    def _type(spell_id: int, effect: Effect) -> TypeEffect | None:
        return TypeEffect.MALUS_LIFE_PERCENT

    def _malus(life_point: int, effect: Effect) -> int:
        return malus

    monkeypatch.setattr(weight_calculator, "get_type_effect", _type)
    monkeypatch.setattr(weight_calculator, "get_life_point_percent_malus", _malus)


def _stub_malus_life_percent_pct(monkeypatch: pytest.MonkeyPatch, pct: float) -> None:
    """Apply a malus computed as `pct` of current life_point at call time."""

    def _type(spell_id: int, effect: Effect) -> TypeEffect | None:
        return TypeEffect.MALUS_LIFE_PERCENT

    def _malus(life_point: int, effect: Effect) -> int:
        return int(life_point * pct)

    monkeypatch.setattr(weight_calculator, "get_type_effect", _type)
    monkeypatch.setattr(weight_calculator, "get_life_point_percent_malus", _malus)


@pytest.fixture(autouse=True)
def patch_singletons(monkeypatch: pytest.MonkeyPatch) -> dict[str, str]:
    """Stub the DataReader / I18N singletons the calculator uses for life-steal detection."""
    state: dict[str, str] = {"description": "physical damage"}

    fake_data_effect = SimpleNamespace(descriptionId=42, characteristicOperator="")
    fake_data_reader = SimpleNamespace(effect_by_id={1: fake_data_effect})
    monkeypatch.setattr(weight_calculator, "DataReader", lambda: fake_data_reader)

    monkeypatch.setattr(effect_module, "DataReader", lambda: fake_data_reader)
    monkeypatch.setattr(
        weight_calculator,
        "I18N",
        lambda: SimpleNamespace(name_by_id={42: state["description"]}),
    )
    return state


def _make_spell(effects: list[Effect]) -> SpellLevelsRootItem:
    return make_spell_level(effects=effects)


class TestCalculateAttackWeight:
    def test_zone_damage_decrease_cap_uses_step_count(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _stub_no_type_effect(monkeypatch)

        effect = _make_effect(step_percent=20, max_apply=2)
        spell_lvl = _make_spell([effect])

        damage_calculator = MagicMock()
        damage_calculator.get_damage_effect.return_value = 100

        target_mp = MapPoint.from_cell_id(0)
        far_enemy = _make_enemy(cell_id=10)
        distance = target_mp.distance_to_map_point(far_enemy.map_point)
        assert distance > effect.zoneDescr.maxDamageDecreaseApplyCount

        weight = calculate_attack_weight(
            damage_calculator=damage_calculator,
            context=_make_context(),
            impact_mps={far_enemy.map_point},
            spell_lvl=spell_lvl,
            effect=effect,
            target_mp=target_mp,
            enemies_data=[far_enemy],
            modifiers=_make_modifiers(ap_cost=1),
        )

        assert weight == pytest.approx(60.0)  # pyright: ignore[reportUnknownMemberType]

    def test_catastrophic_life_cost_drops_weight_below_zero(self, monkeypatch: pytest.MonkeyPatch) -> None:

        _stub_malus_life_percent_pct(monkeypatch, 1.0)

        effect = _make_effect()
        spell_lvl = _make_spell([effect])

        damage_calculator = MagicMock()
        damage_calculator.get_damage_effect.return_value = 100

        enemy = _make_enemy(cell_id=1)
        weight = calculate_attack_weight(
            damage_calculator=damage_calculator,
            context=_make_context(),
            impact_mps={enemy.map_point},
            spell_lvl=spell_lvl,
            effect=effect,
            target_mp=MapPoint.from_cell_id(0),
            enemies_data=[enemy],
            modifiers=_make_modifiers(ap_cost=2),
        )

        assert weight == pytest.approx(-50.0)  # pyright: ignore[reportUnknownMemberType]
        assert weight <= 0

    def test_life_steal_overkill_is_capped(
        self,
        monkeypatch: pytest.MonkeyPatch,
        patch_singletons: dict[str, str],
    ) -> None:
        patch_singletons["description"] = "Vol de vie"
        _stub_no_type_effect(monkeypatch)

        effect = _make_effect()
        spell_lvl = _make_spell([effect])

        damage_calculator = MagicMock()
        damage_calculator.get_damage_effect.return_value = 200

        context = _make_context(life_point=500, max_life_point=1000)
        enemy = _make_enemy(cell_id=1, life_point=50, max_life_point=500)

        weight = calculate_attack_weight(
            damage_calculator=damage_calculator,
            context=context,
            impact_mps={enemy.map_point},
            spell_lvl=spell_lvl,
            effect=effect,
            target_mp=MapPoint.from_cell_id(0),
            enemies_data=[enemy],
            modifiers=_make_modifiers(ap_cost=1),
        )

        assert weight == pytest.approx(1000 * 1.05)  # pyright: ignore[reportUnknownMemberType]

    def test_low_hp_target_is_prioritized_over_full_hp(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """The 1/normalized_health amplifier biases scoring toward finishing wounded enemies."""
        _stub_no_type_effect(monkeypatch)

        effect = _make_effect()
        spell_lvl = _make_spell([effect])

        damage_calculator = MagicMock()
        damage_calculator.get_damage_effect.return_value = 100

        low_hp_enemy = _make_enemy(cell_id=1, life_point=10, max_life_point=500)
        full_hp_enemy = _make_enemy(cell_id=2, life_point=500, max_life_point=500)
        target_mp = MapPoint.from_cell_id(0)

        weight_low = calculate_attack_weight(
            damage_calculator=damage_calculator,
            context=_make_context(),
            impact_mps={low_hp_enemy.map_point},
            spell_lvl=spell_lvl,
            effect=effect,
            target_mp=target_mp,
            enemies_data=[low_hp_enemy],
            modifiers=_make_modifiers(ap_cost=1),
        )
        weight_full = calculate_attack_weight(
            damage_calculator=damage_calculator,
            context=_make_context(),
            impact_mps={full_hp_enemy.map_point},
            spell_lvl=spell_lvl,
            effect=effect,
            target_mp=target_mp,
            enemies_data=[full_hp_enemy],
            modifiers=_make_modifiers(ap_cost=1),
        )

        assert weight_low == pytest.approx(1000.0)  # pyright: ignore[reportUnknownMemberType]
        assert weight_full == pytest.approx(100.0)  # pyright: ignore[reportUnknownMemberType]
        assert weight_low > weight_full

    def test_multiple_malus_life_percent_effects_are_summed(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _stub_malus_life_percent(monkeypatch, malus=100)

        effect_a = _make_effect()
        effect_b = _make_effect()
        spell_lvl = _make_spell([effect_a, effect_b])

        life_malus, _ = weight_calculator.calculate_life_modifiers(_make_context(), spell_lvl)
        assert life_malus == 200

    def test_summoned_enemy_has_lower_weight_than_regular(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _stub_no_type_effect(monkeypatch)

        effect = _make_effect()
        spell_lvl = _make_spell([effect])

        damage_calculator = MagicMock()
        damage_calculator.get_damage_effect.return_value = 1000

        summon = _make_enemy(cell_id=1, life_point=100, max_life_point=100, is_summoned=True)
        regular = _make_enemy(cell_id=2, life_point=100, max_life_point=100, is_summoned=False)
        target_mp = MapPoint.from_cell_id(0)

        weight_summon = calculate_attack_weight(
            damage_calculator=damage_calculator,
            context=_make_context(),
            impact_mps={summon.map_point},
            spell_lvl=spell_lvl,
            effect=effect,
            target_mp=target_mp,
            enemies_data=[summon],
            modifiers=_make_modifiers(ap_cost=1),
        )
        weight_regular = calculate_attack_weight(
            damage_calculator=damage_calculator,
            context=_make_context(),
            impact_mps={regular.map_point},
            spell_lvl=spell_lvl,
            effect=effect,
            target_mp=target_mp,
            enemies_data=[regular],
            modifiers=_make_modifiers(ap_cost=1),
        )

        assert weight_summon == pytest.approx(75.0)  # pyright: ignore[reportUnknownMemberType]
        assert weight_regular == pytest.approx(200.0)  # pyright: ignore[reportUnknownMemberType]
        assert weight_summon < weight_regular

    def test_invulnerable_enemy_is_not_targeted(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Damage on a fully invulnerable target is wasted -> zero weight."""
        _stub_no_type_effect(monkeypatch)

        effect = _make_effect()
        spell_lvl = _make_spell([effect])

        damage_calculator = MagicMock()
        damage_calculator.get_damage_effect.return_value = 1000

        enemy = _make_enemy(cell_id=1, state_ids=frozenset({56}))
        weight = calculate_attack_weight(
            damage_calculator=damage_calculator,
            context=_make_context(),
            impact_mps={enemy.map_point},
            spell_lvl=spell_lvl,
            effect=effect,
            target_mp=MapPoint.from_cell_id(0),
            enemies_data=[enemy],
            modifiers=_make_modifiers(ap_cost=1),
        )

        assert weight == 0.0

    def test_invisible_enemy_is_not_targeted(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """An invisible (non-detected) target cannot be reliably hit -> zero weight."""
        _stub_no_type_effect(monkeypatch)

        effect = _make_effect()
        spell_lvl = _make_spell([effect])

        damage_calculator = MagicMock()
        damage_calculator.get_damage_effect.return_value = 1000

        enemy = _make_enemy(cell_id=1, invisibility=FightInvisibilityState.INVISIBLE)
        weight = calculate_attack_weight(
            damage_calculator=damage_calculator,
            context=_make_context(),
            impact_mps={enemy.map_point},
            spell_lvl=spell_lvl,
            effect=effect,
            target_mp=MapPoint.from_cell_id(0),
            enemies_data=[enemy],
            modifiers=_make_modifiers(ap_cost=1),
        )

        assert weight == 0.0

    def test_bi_element_spell_sums_both_damage_effects(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """A spell with two co-zone damage effects is valued by their sum."""
        _stub_no_type_effect(monkeypatch)

        effect_str = _make_effect()
        effect_int = msgspec.structs.replace(effect_str, effectElement=EffectElement.INTELLIGENCE)
        spell_lvl = _make_spell([effect_str, effect_int])

        damage_calculator = MagicMock()
        damage_calculator.get_damage_effect.return_value = 100

        enemy = _make_enemy(cell_id=1, life_point=1000, max_life_point=1000)
        weight = calculate_attack_weight(
            damage_calculator=damage_calculator,
            context=_make_context(),
            impact_mps={enemy.map_point},
            spell_lvl=spell_lvl,
            effect=effect_str,
            target_mp=MapPoint.from_cell_id(0),
            enemies_data=[enemy],
            modifiers=_make_modifiers(ap_cost=1),
        )

        assert weight == pytest.approx(200.0)  # pyright: ignore[reportUnknownMemberType]

    def test_ally_only_effect_is_not_counted_as_enemy_damage(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Absorption-like ally transfer effects must not inflate attack weight."""
        _stub_no_type_effect(monkeypatch)

        enemy_damage_effect = _make_effect()
        ally_transfer_effect = msgspec.structs.replace(
            enemy_damage_effect,
            effectElement=EffectElement.CHANCE,
            targetMask="a",
        )
        spell_lvl = _make_spell([enemy_damage_effect, ally_transfer_effect])

        damage_calculator = MagicMock()
        damage_calculator.get_damage_effect.return_value = 100

        enemy = _make_enemy(cell_id=1, life_point=1000, max_life_point=1000)
        weight = calculate_attack_weight(
            damage_calculator=damage_calculator,
            context=_make_context(),
            impact_mps={enemy.map_point},
            spell_lvl=spell_lvl,
            effect=enemy_damage_effect,
            target_mp=MapPoint.from_cell_id(0),
            enemies_data=[enemy],
            modifiers=_make_modifiers(ap_cost=1),
        )

        assert weight == pytest.approx(100.0)  # pyright: ignore[reportUnknownMemberType]
        assert damage_calculator.get_damage_effect.call_count == 1

    def test_mixed_ally_enemy_effect_is_counted_as_enemy_damage(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _stub_no_type_effect(monkeypatch)

        mixed_effect = msgspec.structs.replace(_make_effect(), targetMask="a,A")
        spell_lvl = _make_spell([mixed_effect])

        damage_calculator = MagicMock()
        damage_calculator.get_damage_effect.return_value = 100

        enemy = _make_enemy(cell_id=1, life_point=1000, max_life_point=1000)
        weight = calculate_attack_weight(
            damage_calculator=damage_calculator,
            context=_make_context(),
            impact_mps={enemy.map_point},
            spell_lvl=spell_lvl,
            effect=mixed_effect,
            target_mp=MapPoint.from_cell_id(0),
            enemies_data=[enemy],
            modifiers=_make_modifiers(ap_cost=1),
        )

        assert weight == pytest.approx(100.0)  # pyright: ignore[reportUnknownMemberType]

    def test_ally_in_aoe_penalises_weight(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """An AoE catching an ally is strongly down-weighted."""
        _stub_no_type_effect(monkeypatch)

        effect = _make_effect()
        spell_lvl = _make_spell([effect])

        damage_calculator = MagicMock()
        damage_calculator.get_damage_effect.return_value = 100

        enemy = _make_enemy(cell_id=1, life_point=1000, max_life_point=1000)
        ally = _make_actor(actor_id=3, cell_id=2)
        enemy_actor = _make_actor(actor_id=2, cell_id=1)
        context = _make_context(
            actor_by_id={2: enemy_actor, 3: ally},
            enemy_actors=[enemy_actor],
        )

        weight = calculate_attack_weight(
            damage_calculator=damage_calculator,
            context=context,
            impact_mps={MapPoint.from_cell_id(1), MapPoint.from_cell_id(2)},
            spell_lvl=spell_lvl,
            effect=effect,
            target_mp=MapPoint.from_cell_id(1),
            enemies_data=[enemy],
            modifiers=_make_modifiers(ap_cost=1),
        )

        assert weight == pytest.approx(10.0)  # pyright: ignore[reportUnknownMemberType]
