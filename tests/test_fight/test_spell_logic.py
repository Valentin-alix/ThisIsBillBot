import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from dofus_unity_reader.enums.effect_element import EffectElement
from dofus_unity_reader.grid.map_point import MapPoint
from dofus_unity_reader.models.datas.spell_levels_root import (
    Effect,
    SpellLevelsRootItem,
)
from dofus_unity_reader.models.datas.zone_descr import ZoneDescr
from datas.protos.non_obf.game.common_pb2 import SpellModifier
from datas.protos.non_obf.game.spell_pb2 import SpellItem

from src.core.engine.fights.spell import get_damage_spells, get_possible_mp_spell


def _make_zone_descr() -> ZoneDescr:
    return ZoneDescr(
        cellIds=[],
        shape=0,
        param1=0,
        param2=0,
        damageDecreaseStepPercent=0,
        maxDamageDecreaseApplyCount=0,
        isStopAtTarget=0,
    )


def _make_effect(effect_id: int, effect_element: EffectElement) -> Effect:
    return Effect(
        m_flags=0,
        effectUid=effect_id,
        baseEffectId=effect_id,
        effectId=effect_id,
        order=0,
        targetId=0,
        targetMask="",
        duration=0,
        random=0,
        group=0,
        modificator=0,
        dispellable=0,
        delay=0,
        triggers="",
        effectElement=effect_element,
        spellId=1,
        effectTriggerDuration=0,
        zoneDescr=_make_zone_descr(),
        value=0,
        diceNum=0,
        diceSide=0,
        displayZero=0,
    )


def _make_spell_level(
    *,
    range_value: int = 0,
    min_range: int = 0,
    flags: int = 0,
    states_criterion: str = "",
    global_cooldown: int = 0,
    initial_cooldown: int = 0,
    effects: list[Effect] | None = None,
) -> SpellLevelsRootItem:
    return SpellLevelsRootItem(
        m_flags=flags,
        id=1,
        spellId=1,
        grade=1,
        spellBreed=0,
        apCost=3,
        minRange=min_range,
        range=range_value,
        criticalHitProbability=0,
        maxStack=0,
        maxCastPerTurn=0,
        maxCastPerTarget=0,
        minCastInterval=0,
        initialCooldown=initial_cooldown,
        globalCooldown=global_cooldown,
        minPlayerLevel=1,
        statesCriterion=states_criterion,
        effects=effects or [],
        criticalEffect=[],
        previewZones=[],
    )


class TestSpellLogic(unittest.TestCase):
    @patch("src.core.engine.fights.spell.Cross")
    def test_get_possible_mp_spell_uses_cross_for_line_spells(
        self, mock_cross_class: MagicMock
    ) -> None:
        origin = MapPoint.from_cell_id(0)
        expected = {MapPoint.from_cell_id(1)}
        mock_cross = MagicMock()
        mock_cross.get_mps.return_value = expected
        mock_cross_class.return_value = mock_cross

        result = get_possible_mp_spell(
            origin=origin,
            spell_lvl=_make_spell_level(range_value=5, min_range=2, flags=1),
            stat_po=3,
            modifier_range_min=None,
            modifier_range_max=None,
            modifier_cast_line=None,
        )

        mock_cross_class.assert_called_once_with(shape=None, alternative_size=2, size=5)
        mock_cross.get_mps.assert_called_once_with(mp=origin, direction=None)
        self.assertEqual(result, expected)

    @patch("src.core.engine.fights.spell.Cross")
    def test_get_possible_mp_spell_uses_diagonal_cross_when_needed(
        self, mock_cross_class: MagicMock
    ) -> None:
        origin = MapPoint.from_cell_id(0)
        expected = {MapPoint.from_cell_id(1)}
        mock_cross = MagicMock()
        mock_cross.get_mps.return_value = expected
        mock_cross_class.return_value = mock_cross

        result = get_possible_mp_spell(
            origin=origin,
            spell_lvl=_make_spell_level(range_value=5, min_range=1, flags=2),
            stat_po=0,
            modifier_range_min=SpellModifier(context=3),
            modifier_range_max=SpellModifier(context=7),
            modifier_cast_line=None,
        )

        mock_cross_class.assert_called_once_with(
            shape=None,
            alternative_size=3,
            size=7,
            is_all_directions=True,
            is_diagonal=True,
        )
        mock_cross.get_mps.assert_called_once_with(mp=origin, direction=None)
        self.assertEqual(result, expected)

    @patch("src.core.engine.fights.spell.Lozenge")
    def test_get_possible_mp_spell_uses_lozenge_by_default(
        self, mock_lozenge_class: MagicMock
    ) -> None:
        origin = MapPoint.from_cell_id(0)
        expected = {MapPoint.from_cell_id(1)}
        mock_lozenge = MagicMock()
        mock_lozenge.get_mps.return_value = expected
        mock_lozenge_class.return_value = mock_lozenge

        result = get_possible_mp_spell(
            origin=origin,
            spell_lvl=_make_spell_level(range_value=4, min_range=0, flags=0),
            stat_po=0,
            modifier_range_min=None,
            modifier_range_max=None,
            modifier_cast_line=SpellModifier(context=0),
        )

        mock_lozenge_class.assert_called_once_with(alternative_size=0, size=4)
        mock_lozenge.get_mps.assert_called_once_with(origin, direction=None)
        self.assertEqual(result, expected)

    @patch("src.core.engine.fights.spell.DataReader")
    def test_get_damage_spells_filters_invalid_spells_and_limits_secondary(
        self, mock_data_reader_class: MagicMock
    ) -> None:
        effect_primary = _make_effect(1, EffectElement.CHANCE)
        effect_secondary_one = _make_effect(2, EffectElement.AGILITY)
        effect_secondary_two = _make_effect(3, EffectElement.AGILITY)
        effect_secondary_three = _make_effect(4, EffectElement.AGILITY)
        effect_invalid_operator = _make_effect(5, EffectElement.CHANCE)

        spell_level_primary = _make_spell_level(
            effects=[effect_invalid_operator, effect_primary]
        )
        spell_level_secondary_one = _make_spell_level(effects=[effect_secondary_one])
        spell_level_secondary_two = _make_spell_level(effects=[effect_secondary_two])
        spell_level_secondary_three = _make_spell_level(
            effects=[effect_secondary_three]
        )
        spell_level_with_state = _make_spell_level(
            states_criterion="state",
            effects=[effect_primary],
        )
        spell_level_with_cooldown = _make_spell_level(
            global_cooldown=1,
            effects=[effect_primary],
        )

        mock_data_reader = MagicMock()
        mock_data_reader.spell_lvl_by_spell_id = {
            10: [spell_level_primary],
            11: [spell_level_secondary_one],
            12: [spell_level_secondary_two],
            13: [spell_level_secondary_three],
            14: [spell_level_with_state],
            15: [spell_level_with_cooldown],
        }
        mock_data_reader.effect_by_id = {
            1: SimpleNamespace(characteristicOperator=""),
            2: SimpleNamespace(characteristicOperator=""),
            3: SimpleNamespace(characteristicOperator=""),
            4: SimpleNamespace(characteristicOperator=""),
            5: SimpleNamespace(characteristicOperator="+"),
        }
        mock_data_reader_class.return_value = mock_data_reader

        result = get_damage_spells(
            [
                SpellItem(spell_id=0, spell_level=1),
                SpellItem(spell_id=10, spell_level=1),
                SpellItem(spell_id=11, spell_level=1),
                SpellItem(spell_id=12, spell_level=1),
                SpellItem(spell_id=13, spell_level=1),
                SpellItem(spell_id=14, spell_level=1),
                SpellItem(spell_id=15, spell_level=1),
            ],
            primary_elem=EffectElement.CHANCE,
            secondary_elem=EffectElement.AGILITY,
        )

        self.assertEqual(
            result,
            [
                (spell_level_primary, effect_primary),
                (spell_level_secondary_one, effect_secondary_one),
                (spell_level_secondary_two, effect_secondary_two),
            ],
        )
