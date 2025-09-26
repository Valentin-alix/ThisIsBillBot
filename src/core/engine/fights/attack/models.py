from dataclasses import dataclass, field
from enum import StrEnum, auto

from datas.protos.non_obf.game.common_pb2 import (
    ActorPositionInformation,
    FightInvisibilityState,
)
from dofus_unity_reader.game_constants.spell_state import SpellStateEnum
from dofus_unity_reader.grid.map_point import MapPoint
from dofus_unity_reader.models.datas.monsters_root import MonsterGrade


FULLY_INVULNERABLE_STATE_IDS: frozenset[int] = frozenset(
    {
        SpellStateEnum.INVULNERABLE,
        SpellStateEnum.INVULNERABLE_269,
        SpellStateEnum.INVULNERABLE_365,
        SpellStateEnum.INVULNERABLE_399,
        SpellStateEnum.INVULNERABLE_659,
    }
)


class AttackWeights:
    LIFE_RECOVERY_MULTIPLIER = 2
    LIFE_STEAL_RATIO = 0.5
    ENEMY_KILL_BONUS = 1.0
    SUMMONED_KILL_BONUS = 0.5
    SUMMONED_DAMAGE_DIVISOR = 2

    ALLY_HIT_PENALTY_FACTOR = 0.1


class RejectionStat(StrEnum):
    MAX_CAST_PER_TARGET = auto()
    MAX_CAST_PER_TURN = auto()
    INSUFICIENT_AP = auto()
    INITIAL_COOLDOWN = auto()
    GLOBAL_COOLDOWN = auto()
    CELL_NOT_WALKABLE = auto()
    NO_LOS = auto()


@dataclass
class EnemyData:
    actor: ActorPositionInformation
    map_point: MapPoint
    life_point: int
    max_life_point: int
    is_summoned: bool
    monster_grade: MonsterGrade
    invisibility: FightInvisibilityState = FightInvisibilityState.VISIBLE
    state_ids: frozenset[int] = field(default_factory=frozenset[int])

    @property
    def is_invulnerable(self) -> bool:
        return bool(self.state_ids & FULLY_INVULNERABLE_STATE_IDS)

    @property
    def is_hidden(self) -> bool:
        return self.invisibility == FightInvisibilityState.INVISIBLE
