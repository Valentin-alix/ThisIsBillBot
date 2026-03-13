from dataclasses import dataclass, field

from DBDofusUnity.datas.protos.non_obf.game.common_pb2 import (
    ActorPositionInformation,
    FightInvisibilityState,
)
from DBDofusUnity.dofus_unity_reader.data_center.data_reader import DataReader
from DBDofusUnity.dofus_unity_reader.game_constants.spell_state import SpellStateEnum
from DBDofusUnity.dofus_unity_reader.grid.map_point import MapPoint
from DBDofusUnity.dofus_unity_reader.models.datas.monsters_root import MonsterGrade, MonsterItem

FULLY_INVULNERABLE_STATE_IDS: frozenset[int] = frozenset(
    {
        SpellStateEnum.INVULNERABLE,
        SpellStateEnum.INVULNERABLE_269,
        SpellStateEnum.INVULNERABLE_365,
        SpellStateEnum.INVULNERABLE_399,
        SpellStateEnum.INVULNERABLE_659,
    }
)


@dataclass
class EnemyData:
    actor: ActorPositionInformation
    map_point: MapPoint
    life_point: int
    max_life_point: int
    is_summoned: bool
    monster_grade: MonsterGrade
    movement_points: int
    max_spell_range: int
    invisibility: FightInvisibilityState = FightInvisibilityState.VISIBLE
    state_ids: frozenset[int] = field(default_factory=frozenset[int])

    @property
    def is_invulnerable(self) -> bool:
        return bool(self.state_ids & FULLY_INVULNERABLE_STATE_IDS)

    @property
    def is_hidden(self) -> bool:
        return self.invisibility == FightInvisibilityState.INVISIBLE


def get_monster_max_spell_range(monster: MonsterItem, monster_grade: MonsterGrade) -> int:
    """Use all known spell levels because spellGrades is unavailable; range is an overestimate."""
    spell_lvl_by_spell_id = DataReader().spell_lvl_by_spell_id
    max_range = max(
        (
            spell_lvl.range
            for spell_id in monster.spells
            for spell_lvl in spell_lvl_by_spell_id.get(spell_id, [])
        ),
        default=0,
    )
    return max_range + monster_grade.bonusRange
