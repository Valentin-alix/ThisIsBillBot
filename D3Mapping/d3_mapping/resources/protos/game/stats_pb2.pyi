import common_pb2 as _common_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FighterIdentity(_message.Message):
    __slots__ = ("player_id", "team", "player", "monster", "companion", "summon")
    class Player(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class Monster(_message.Message):
        __slots__ = ("esag",)
        ESAG_FIELD_NUMBER: _ClassVar[int]
        esag: int
        def __init__(self, esag: _Optional[int] = ...) -> None: ...
    class Companion(_message.Message):
        __slots__ = ("esak", "entity")
        ESAK_FIELD_NUMBER: _ClassVar[int]
        ENTITY_FIELD_NUMBER: _ClassVar[int]
        esak: int
        entity: FighterIdentity
        def __init__(self, esak: _Optional[int] = ..., entity: _Optional[_Union[FighterIdentity, _Mapping]] = ...) -> None: ...
    class Summon(_message.Message):
        __slots__ = ("esap", "entity")
        ESAP_FIELD_NUMBER: _ClassVar[int]
        ENTITY_FIELD_NUMBER: _ClassVar[int]
        esap: int
        entity: FighterIdentity
        def __init__(self, esap: _Optional[int] = ..., entity: _Optional[_Union[FighterIdentity, _Mapping]] = ...) -> None: ...
    PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
    TEAM_FIELD_NUMBER: _ClassVar[int]
    PLAYER_FIELD_NUMBER: _ClassVar[int]
    MONSTER_FIELD_NUMBER: _ClassVar[int]
    COMPANION_FIELD_NUMBER: _ClassVar[int]
    SUMMON_FIELD_NUMBER: _ClassVar[int]
    player_id: int
    team: _common_pb2.Team
    player: FighterIdentity.Player
    monster: FighterIdentity.Monster
    companion: FighterIdentity.Companion
    summon: FighterIdentity.Summon
    def __init__(self, player_id: _Optional[int] = ..., team: _Optional[_Union[_common_pb2.Team, str]] = ..., player: _Optional[_Union[FighterIdentity.Player, _Mapping]] = ..., monster: _Optional[_Union[FighterIdentity.Monster, _Mapping]] = ..., companion: _Optional[_Union[FighterIdentity.Companion, _Mapping]] = ..., summon: _Optional[_Union[FighterIdentity.Summon, _Mapping]] = ...) -> None: ...

class BaseStatistics(_message.Message):
    __slots__ = ("damage_done", "damage_taken", "blocked_damage", "applied_shield", "heal_done", "heal_taken", "kill_count")
    DAMAGE_DONE_FIELD_NUMBER: _ClassVar[int]
    DAMAGE_TAKEN_FIELD_NUMBER: _ClassVar[int]
    BLOCKED_DAMAGE_FIELD_NUMBER: _ClassVar[int]
    APPLIED_SHIELD_FIELD_NUMBER: _ClassVar[int]
    HEAL_DONE_FIELD_NUMBER: _ClassVar[int]
    HEAL_TAKEN_FIELD_NUMBER: _ClassVar[int]
    KILL_COUNT_FIELD_NUMBER: _ClassVar[int]
    damage_done: int
    damage_taken: int
    blocked_damage: int
    applied_shield: int
    heal_done: int
    heal_taken: int
    kill_count: int
    def __init__(self, damage_done: _Optional[int] = ..., damage_taken: _Optional[int] = ..., blocked_damage: _Optional[int] = ..., applied_shield: _Optional[int] = ..., heal_done: _Optional[int] = ..., heal_taken: _Optional[int] = ..., kill_count: _Optional[int] = ...) -> None: ...

class DetailedStatistics(_message.Message):
    __slots__ = ("damage_done", "damage_taken", "heal_done", "heal_taken", "shield_done", "shield_taken", "ap_stat_removed", "mp_stat_removed", "kill", "entity")
    class DamageDone(_message.Message):
        __slots__ = ("total", "by_poison", "by_pushing", "by_ground_object", "by_summon", "on_shield", "by_ap_action", "by_turn", "erosion_done")
        TOTAL_FIELD_NUMBER: _ClassVar[int]
        BY_POISON_FIELD_NUMBER: _ClassVar[int]
        BY_PUSHING_FIELD_NUMBER: _ClassVar[int]
        BY_GROUND_OBJECT_FIELD_NUMBER: _ClassVar[int]
        BY_SUMMON_FIELD_NUMBER: _ClassVar[int]
        ON_SHIELD_FIELD_NUMBER: _ClassVar[int]
        BY_AP_ACTION_FIELD_NUMBER: _ClassVar[int]
        BY_TURN_FIELD_NUMBER: _ClassVar[int]
        EROSION_DONE_FIELD_NUMBER: _ClassVar[int]
        total: int
        by_poison: int
        by_pushing: int
        by_ground_object: int
        by_summon: int
        on_shield: int
        by_ap_action: float
        by_turn: float
        erosion_done: int
        def __init__(self, total: _Optional[int] = ..., by_poison: _Optional[int] = ..., by_pushing: _Optional[int] = ..., by_ground_object: _Optional[int] = ..., by_summon: _Optional[int] = ..., on_shield: _Optional[int] = ..., by_ap_action: _Optional[float] = ..., by_turn: _Optional[float] = ..., erosion_done: _Optional[int] = ...) -> None: ...
    class DamageTaken(_message.Message):
        __slots__ = ("total", "by_poison", "by_pushing", "by_ground_object", "by_summon", "on_shield", "by_turn", "erosion_done")
        TOTAL_FIELD_NUMBER: _ClassVar[int]
        BY_POISON_FIELD_NUMBER: _ClassVar[int]
        BY_PUSHING_FIELD_NUMBER: _ClassVar[int]
        BY_GROUND_OBJECT_FIELD_NUMBER: _ClassVar[int]
        BY_SUMMON_FIELD_NUMBER: _ClassVar[int]
        ON_SHIELD_FIELD_NUMBER: _ClassVar[int]
        BY_TURN_FIELD_NUMBER: _ClassVar[int]
        EROSION_DONE_FIELD_NUMBER: _ClassVar[int]
        total: int
        by_poison: int
        by_pushing: int
        by_ground_object: int
        by_summon: int
        on_shield: int
        by_turn: float
        erosion_done: int
        def __init__(self, total: _Optional[int] = ..., by_poison: _Optional[int] = ..., by_pushing: _Optional[int] = ..., by_ground_object: _Optional[int] = ..., by_summon: _Optional[int] = ..., on_shield: _Optional[int] = ..., by_turn: _Optional[float] = ..., erosion_done: _Optional[int] = ...) -> None: ...
    class HealDone(_message.Message):
        __slots__ = ("total", "by_summon", "by_ap_action", "by_turn")
        TOTAL_FIELD_NUMBER: _ClassVar[int]
        BY_SUMMON_FIELD_NUMBER: _ClassVar[int]
        BY_AP_ACTION_FIELD_NUMBER: _ClassVar[int]
        BY_TURN_FIELD_NUMBER: _ClassVar[int]
        total: int
        by_summon: int
        by_ap_action: float
        by_turn: float
        def __init__(self, total: _Optional[int] = ..., by_summon: _Optional[int] = ..., by_ap_action: _Optional[float] = ..., by_turn: _Optional[float] = ...) -> None: ...
    class HealTaken(_message.Message):
        __slots__ = ("total", "by_summon", "by_turn")
        TOTAL_FIELD_NUMBER: _ClassVar[int]
        BY_SUMMON_FIELD_NUMBER: _ClassVar[int]
        BY_TURN_FIELD_NUMBER: _ClassVar[int]
        total: int
        by_summon: int
        by_turn: float
        def __init__(self, total: _Optional[int] = ..., by_summon: _Optional[int] = ..., by_turn: _Optional[float] = ...) -> None: ...
    class ShieldDone(_message.Message):
        __slots__ = ("total", "by_summon", "by_turn")
        TOTAL_FIELD_NUMBER: _ClassVar[int]
        BY_SUMMON_FIELD_NUMBER: _ClassVar[int]
        BY_TURN_FIELD_NUMBER: _ClassVar[int]
        total: int
        by_summon: int
        by_turn: float
        def __init__(self, total: _Optional[int] = ..., by_summon: _Optional[int] = ..., by_turn: _Optional[float] = ...) -> None: ...
    class ShieldTaken(_message.Message):
        __slots__ = ("total", "by_summon", "by_turn")
        TOTAL_FIELD_NUMBER: _ClassVar[int]
        BY_SUMMON_FIELD_NUMBER: _ClassVar[int]
        BY_TURN_FIELD_NUMBER: _ClassVar[int]
        total: int
        by_summon: int
        by_turn: float
        def __init__(self, total: _Optional[int] = ..., by_summon: _Optional[int] = ..., by_turn: _Optional[float] = ...) -> None: ...
    class StatRemoved(_message.Message):
        __slots__ = ("dodged", "not_dodged", "removed", "average_dodged_by_turn", "average_not_dodged_by_turn", "average_removed_by_turn", "average_spent_by_turn")
        DODGED_FIELD_NUMBER: _ClassVar[int]
        NOT_DODGED_FIELD_NUMBER: _ClassVar[int]
        REMOVED_FIELD_NUMBER: _ClassVar[int]
        AVERAGE_DODGED_BY_TURN_FIELD_NUMBER: _ClassVar[int]
        AVERAGE_NOT_DODGED_BY_TURN_FIELD_NUMBER: _ClassVar[int]
        AVERAGE_REMOVED_BY_TURN_FIELD_NUMBER: _ClassVar[int]
        AVERAGE_SPENT_BY_TURN_FIELD_NUMBER: _ClassVar[int]
        dodged: int
        not_dodged: int
        removed: int
        average_dodged_by_turn: float
        average_not_dodged_by_turn: float
        average_removed_by_turn: float
        average_spent_by_turn: float
        def __init__(self, dodged: _Optional[int] = ..., not_dodged: _Optional[int] = ..., removed: _Optional[int] = ..., average_dodged_by_turn: _Optional[float] = ..., average_not_dodged_by_turn: _Optional[float] = ..., average_removed_by_turn: _Optional[float] = ..., average_spent_by_turn: _Optional[float] = ...) -> None: ...
    class Kill(_message.Message):
        __slots__ = ("total", "enemies", "enemies_summon")
        TOTAL_FIELD_NUMBER: _ClassVar[int]
        ENEMIES_FIELD_NUMBER: _ClassVar[int]
        ENEMIES_SUMMON_FIELD_NUMBER: _ClassVar[int]
        total: int
        enemies: int
        enemies_summon: int
        def __init__(self, total: _Optional[int] = ..., enemies: _Optional[int] = ..., enemies_summon: _Optional[int] = ...) -> None: ...
    DAMAGE_DONE_FIELD_NUMBER: _ClassVar[int]
    DAMAGE_TAKEN_FIELD_NUMBER: _ClassVar[int]
    HEAL_DONE_FIELD_NUMBER: _ClassVar[int]
    HEAL_TAKEN_FIELD_NUMBER: _ClassVar[int]
    SHIELD_DONE_FIELD_NUMBER: _ClassVar[int]
    SHIELD_TAKEN_FIELD_NUMBER: _ClassVar[int]
    AP_STAT_REMOVED_FIELD_NUMBER: _ClassVar[int]
    MP_STAT_REMOVED_FIELD_NUMBER: _ClassVar[int]
    KILL_FIELD_NUMBER: _ClassVar[int]
    ENTITY_FIELD_NUMBER: _ClassVar[int]
    damage_done: DetailedStatistics.DamageDone
    damage_taken: DetailedStatistics.DamageTaken
    heal_done: DetailedStatistics.HealDone
    heal_taken: DetailedStatistics.HealTaken
    shield_done: DetailedStatistics.ShieldDone
    shield_taken: DetailedStatistics.ShieldTaken
    ap_stat_removed: DetailedStatistics.StatRemoved
    mp_stat_removed: DetailedStatistics.StatRemoved
    kill: DetailedStatistics.Kill
    entity: FighterIdentity
    def __init__(self, damage_done: _Optional[_Union[DetailedStatistics.DamageDone, _Mapping]] = ..., damage_taken: _Optional[_Union[DetailedStatistics.DamageTaken, _Mapping]] = ..., heal_done: _Optional[_Union[DetailedStatistics.HealDone, _Mapping]] = ..., heal_taken: _Optional[_Union[DetailedStatistics.HealTaken, _Mapping]] = ..., shield_done: _Optional[_Union[DetailedStatistics.ShieldDone, _Mapping]] = ..., shield_taken: _Optional[_Union[DetailedStatistics.ShieldTaken, _Mapping]] = ..., ap_stat_removed: _Optional[_Union[DetailedStatistics.StatRemoved, _Mapping]] = ..., mp_stat_removed: _Optional[_Union[DetailedStatistics.StatRemoved, _Mapping]] = ..., kill: _Optional[_Union[DetailedStatistics.Kill, _Mapping]] = ..., entity: _Optional[_Union[FighterIdentity, _Mapping]] = ...) -> None: ...
