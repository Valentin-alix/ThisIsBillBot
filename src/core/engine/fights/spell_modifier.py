from dataclasses import dataclass

from DBDofusUnity.datas.protos.non_obf.game.common_pb2 import SpellModifier, SpellModifierType
from DBDofusUnity.dofus_unity_reader.models.datas.spell_levels_root import SpellLevelsRootItem

from src.core.engine.fights.spell import (
    get_ap_cost_spell,
    get_max_range_spell,
    get_min_range_spell,
    get_spell_max_cast_per_target,
    get_spell_max_cast_per_turn,
    is_spell_cast_in_line,
)


@dataclass
class SpellModifiers:
    ap_cost: int
    max_cast_per_turn: int
    max_cast_per_target: int
    range_min: int
    range_max: int
    cast_line: int | None

    @classmethod
    def from_spell(
        cls,
        stat_po: int,
        spell_lvl: SpellLevelsRootItem,
        modifiers_map: dict[tuple[int, SpellModifierType], SpellModifier],
    ) -> "SpellModifiers":
        spell_id = spell_lvl.spellId
        return cls(
            ap_cost=get_ap_cost_spell(spell_lvl, modifiers_map.get((spell_id, SpellModifierType.AP_COST))),
            max_cast_per_turn=(
                get_spell_max_cast_per_turn(
                    spell_lvl,
                    modifiers_map.get((spell_id, SpellModifierType.MAX_CAST_PER_TURN)),
                )
            ),
            max_cast_per_target=(
                get_spell_max_cast_per_target(
                    spell_lvl,
                    modifiers_map.get((spell_id, SpellModifierType.MAX_CAST_PER_TARGET)),
                )
            ),
            range_min=get_min_range_spell(
                spell_lvl, modifiers_map.get((spell_id, SpellModifierType.RANGE_MIN))
            ),
            range_max=get_max_range_spell(
                stat_po,
                spell_lvl,
                modifiers_map.get((spell_id, SpellModifierType.RANGE_MAX)),
            ),
            cast_line=is_spell_cast_in_line(
                spell_lvl, modifiers_map.get((spell_id, SpellModifierType.CAST_LINE))
            ),
        )
