from dataclasses import dataclass
from enum import StrEnum, auto

from datas.protos.non_obf.game.common_pb2 import ActorPositionInformation
from dofus_unity_reader.grid.map_point import MapPoint
from dofus_unity_reader.models.datas.monsters_root import MonsterGrade


class AttackWeights:
    LIFE_RECOVERY_MULTIPLIER = 2
    LIFE_STEAL_RATIO = 0.5
    ENEMY_KILL_BONUS = 1.0
    SUMMONED_KILL_BONUS = 0.5
    SUMMONED_ENEMY_PENALTY = 0.5
    SUMMONED_DAMAGE_DIVISOR = 2


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
