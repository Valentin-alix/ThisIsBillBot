from datas.protos.non_obf.game.common_pb2 import SpellModifier
from datas.protos.non_obf.game.spell_pb2 import SpellItem
from dofus_unity_reader.data_center.data_reader import DataReader
from dofus_unity_reader.game_constants.characteristic import EffectElement
from dofus_unity_reader.grid.map_point import MapPoint
from dofus_unity_reader.models.datas.spell_levels_root import (
    Effect,
    SpellLevelsRootItem,
)

from src.core.engine.fights.zones.cross import Cross
from src.core.engine.fights.zones.lozenge import Lozenge


def get_max_range_spell(
    stat_po: int,
    spell_lvl: SpellLevelsRootItem,
    modifier_range_max: SpellModifier | None,
) -> int:
    if modifier_range_max:
        range = modifier_range_max.context
    else:
        range = spell_lvl.range

    if (spell_lvl.m_flags & 64) != 0:
        return range + stat_po

    return range


def get_min_range_spell(
    spell_lvl: SpellLevelsRootItem, modifier_range_min: SpellModifier | None
) -> int:
    if modifier_range_min:
        return modifier_range_min.context

    return spell_lvl.minRange


def get_ap_cost_spell(
    spell_lvl: SpellLevelsRootItem, modifier_ap_cost: SpellModifier | None
) -> int:
    if modifier_ap_cost:
        return modifier_ap_cost.context

    return spell_lvl.apCost


def get_spell_max_cast_per_turn(
    spell_lvl: SpellLevelsRootItem, modifier_max_cast_per_turn: SpellModifier | None
):
    if modifier_max_cast_per_turn:
        return modifier_max_cast_per_turn.context
    return spell_lvl.maxCastPerTurn


def get_spell_max_cast_per_target(
    spell_lvl: SpellLevelsRootItem, modifier_max_cast_per_target: SpellModifier | None
):
    if modifier_max_cast_per_target:
        return modifier_max_cast_per_target.context
    return spell_lvl.maxCastPerTarget


def is_spell_cast_in_line(
    spell_lvl: SpellLevelsRootItem, modifier_cast_line: SpellModifier | None
) -> bool:
    if modifier_cast_line:
        return bool(modifier_cast_line.context)

    # [517, 581, 521, 513, 585]
    if (spell_lvl.m_flags & 1) != 0:
        return True
    return False


def is_spell_cast_in_diagonal(spell_lvl: SpellLevelsRootItem) -> bool:
    if (spell_lvl.m_flags & 2) != 0:
        return True
    return False


def does_spell_need_taken_cell(spell_lvl: SpellLevelsRootItem) -> bool:
    if (spell_lvl.m_flags & 16) != 0:
        return True
    return False


def does_spell_need_test_los(spell_lvl: SpellLevelsRootItem) -> bool:
    if (spell_lvl.m_flags & 4) != 0:
        return True
    return False


def get_possible_mp_spell(
    origin: MapPoint,
    spell_lvl: SpellLevelsRootItem,
    stat_po: int,
    modifier_range_min: SpellModifier | None,
    modifier_range_max: SpellModifier | None,
    modifier_cast_line: SpellModifier | None,
) -> set[MapPoint]:
    min_range = get_min_range_spell(spell_lvl, modifier_range_min)
    max_range = get_max_range_spell(stat_po, spell_lvl, modifier_range_max)

    if is_spell_cast_in_line(spell_lvl, modifier_cast_line):
        cross = Cross(shape=None, alternative_size=min_range, size=max_range)
        possible_mps = cross.get_mps(mp=origin, direction=None)
    elif is_spell_cast_in_diagonal(spell_lvl):
        cross = Cross(
            shape=None,
            alternative_size=min_range,
            size=max_range,
            is_all_directions=True,
            is_diagonal=True,
        )
        possible_mps = cross.get_mps(mp=origin, direction=None)
    else:
        lozenge = Lozenge(alternative_size=min_range, size=max_range)
        possible_mps = lozenge.get_mps(origin, direction=None)

    return possible_mps


def get_damage_spells(
    spells: list[SpellItem], primary_elem: EffectElement, secondary_elem: EffectElement
) -> list[tuple[SpellLevelsRootItem, Effect]]:
    spell_levels: list[tuple[SpellLevelsRootItem, Effect]] = []
    count_secondary_spell_lvl: int = 0
    for spell in spells:
        if not spell.spell_id:
            continue
        spell_lvl = DataReader().spell_lvl_by_spell_id[spell.spell_id][
            spell.spell_level - 1
        ]
        if (
            spell_lvl.statesCriterion != ""
            or spell_lvl.globalCooldown != 0
            or spell_lvl.initialCooldown != 0
        ):
            continue
        for effect in spell_lvl.effects:
            data_effect = DataReader().effect_by_id[effect.effectId]
            if data_effect.characteristicOperator != "":
                continue
            if effect.effectElement == primary_elem:
                spell_levels.append((spell_lvl, effect))
                break
            elif (
                effect.effectElement == secondary_elem and count_secondary_spell_lvl < 2
            ):
                count_secondary_spell_lvl += 1
                spell_levels.append((spell_lvl, effect))
                break

    return spell_levels
