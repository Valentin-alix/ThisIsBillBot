from com.ankama.dofus.server.game.protocol import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FightTurnReadyRequest(_message.Message):
    __slots__ = ("is_ready",)
    IS_READY_FIELD_NUMBER: _ClassVar[int]
    is_ready: bool
    def __init__(self, is_ready: bool = ...) -> None: ...

class FightTurnFinishRequest(_message.Message):
    __slots__ = ("is_afk",)
    IS_AFK_FIELD_NUMBER: _ClassVar[int]
    is_afk: bool
    def __init__(self, is_afk: bool = ...) -> None: ...

class FightJoinRunningEvent(_message.Message):
    __slots__ = ("effects", "marks", "game_turn", "fight_start", "fx_trigger_counts", "resume")
    EFFECTS_FIELD_NUMBER: _ClassVar[int]
    MARKS_FIELD_NUMBER: _ClassVar[int]
    GAME_TURN_FIELD_NUMBER: _ClassVar[int]
    FIGHT_START_FIELD_NUMBER: _ClassVar[int]
    FX_TRIGGER_COUNTS_FIELD_NUMBER: _ClassVar[int]
    RESUME_FIELD_NUMBER: _ClassVar[int]
    effects: _containers.RepeatedCompositeFieldContainer[_common_pb2.FightRemovableEffectExtendedInformation]
    marks: _containers.RepeatedCompositeFieldContainer[_common_pb2.FightMark]
    game_turn: int
    fight_start: int
    fx_trigger_counts: _containers.RepeatedCompositeFieldContainer[_common_pb2.FightEffectTriggerCount]
    resume: FightResume
    def __init__(self, effects: _Optional[_Iterable[_Union[_common_pb2.FightRemovableEffectExtendedInformation, _Mapping]]] = ..., marks: _Optional[_Iterable[_Union[_common_pb2.FightMark, _Mapping]]] = ..., game_turn: _Optional[int] = ..., fight_start: _Optional[int] = ..., fx_trigger_counts: _Optional[_Iterable[_Union[_common_pb2.FightEffectTriggerCount, _Mapping]]] = ..., resume: _Optional[_Union[FightResume, _Mapping]] = ...) -> None: ...

class FightEndEvent(_message.Message):
    __slots__ = ("duration", "reward_rate", "loot_share_limit_malus", "results", "named_party_teams_outcomes", "budget")
    DURATION_FIELD_NUMBER: _ClassVar[int]
    REWARD_RATE_FIELD_NUMBER: _ClassVar[int]
    LOOT_SHARE_LIMIT_MALUS_FIELD_NUMBER: _ClassVar[int]
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    NAMED_PARTY_TEAMS_OUTCOMES_FIELD_NUMBER: _ClassVar[int]
    BUDGET_FIELD_NUMBER: _ClassVar[int]
    duration: int
    reward_rate: int
    loot_share_limit_malus: int
    results: _containers.RepeatedCompositeFieldContainer[_common_pb2.FightResultListEntry]
    named_party_teams_outcomes: _containers.RepeatedCompositeFieldContainer[_common_pb2.NamedPartyTeamWithOutcome]
    budget: int
    def __init__(self, duration: _Optional[int] = ..., reward_rate: _Optional[int] = ..., loot_share_limit_malus: _Optional[int] = ..., results: _Optional[_Iterable[_Union[_common_pb2.FightResultListEntry, _Mapping]]] = ..., named_party_teams_outcomes: _Optional[_Iterable[_Union[_common_pb2.NamedPartyTeamWithOutcome, _Mapping]]] = ..., budget: _Optional[int] = ...) -> None: ...

class FightStatisticsEvent(_message.Message):
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

class FightNewRoundEvent(_message.Message):
    __slots__ = ("round_number",)
    ROUND_NUMBER_FIELD_NUMBER: _ClassVar[int]
    round_number: int
    def __init__(self, round_number: _Optional[int] = ...) -> None: ...

class FightTurnListEvent(_message.Message):
    __slots__ = ("ids", "slain")
    IDS_FIELD_NUMBER: _ClassVar[int]
    SLAIN_FIELD_NUMBER: _ClassVar[int]
    ids: _containers.RepeatedScalarFieldContainer[int]
    slain: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, ids: _Optional[_Iterable[int]] = ..., slain: _Optional[_Iterable[int]] = ...) -> None: ...

class FightTurnEvent(_message.Message):
    __slots__ = ("character_id", "base_time", "extra_time", "remaining_time")
    CHARACTER_ID_FIELD_NUMBER: _ClassVar[int]
    BASE_TIME_FIELD_NUMBER: _ClassVar[int]
    EXTRA_TIME_FIELD_NUMBER: _ClassVar[int]
    REMAINING_TIME_FIELD_NUMBER: _ClassVar[int]
    character_id: int
    base_time: int
    extra_time: int
    remaining_time: int
    def __init__(self, character_id: _Optional[int] = ..., base_time: _Optional[int] = ..., extra_time: _Optional[int] = ..., remaining_time: _Optional[int] = ...) -> None: ...

class FightNewWaveEvent(_message.Message):
    __slots__ = ("wave_id", "team", "turn_left_before_next_wave")
    WAVE_ID_FIELD_NUMBER: _ClassVar[int]
    TEAM_FIELD_NUMBER: _ClassVar[int]
    TURN_LEFT_BEFORE_NEXT_WAVE_FIELD_NUMBER: _ClassVar[int]
    wave_id: int
    team: _common_pb2.Team
    turn_left_before_next_wave: int
    def __init__(self, wave_id: _Optional[int] = ..., team: _Optional[_Union[_common_pb2.Team, str]] = ..., turn_left_before_next_wave: _Optional[int] = ...) -> None: ...

class FightTurnStartPlayingEvent(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class FightPauseEvent(_message.Message):
    __slots__ = ("is_paused",)
    IS_PAUSED_FIELD_NUMBER: _ClassVar[int]
    is_paused: bool
    def __init__(self, is_paused: bool = ...) -> None: ...

class FightScenarioEvent(_message.Message):
    __slots__ = ("scenarios",)
    class ScenarioEntity(_message.Message):
        __slots__ = ("actor_id", "scenario_id")
        ACTOR_ID_FIELD_NUMBER: _ClassVar[int]
        SCENARIO_ID_FIELD_NUMBER: _ClassVar[int]
        actor_id: int
        scenario_id: int
        def __init__(self, actor_id: _Optional[int] = ..., scenario_id: _Optional[int] = ...) -> None: ...
    SCENARIOS_FIELD_NUMBER: _ClassVar[int]
    scenarios: _containers.RepeatedCompositeFieldContainer[FightScenarioEvent.ScenarioEntity]
    def __init__(self, scenarios: _Optional[_Iterable[_Union[FightScenarioEvent.ScenarioEntity, _Mapping]]] = ...) -> None: ...

class FightSlaveSwitchContextEvent(_message.Message):
    __slots__ = ("master_id", "slave_id", "slave_turn", "slave_spells", "slave_stats", "shortcuts")
    MASTER_ID_FIELD_NUMBER: _ClassVar[int]
    SLAVE_ID_FIELD_NUMBER: _ClassVar[int]
    SLAVE_TURN_FIELD_NUMBER: _ClassVar[int]
    SLAVE_SPELLS_FIELD_NUMBER: _ClassVar[int]
    SLAVE_STATS_FIELD_NUMBER: _ClassVar[int]
    SHORTCUTS_FIELD_NUMBER: _ClassVar[int]
    master_id: int
    slave_id: int
    slave_turn: int
    slave_spells: _containers.RepeatedCompositeFieldContainer[_common_pb2.SpellItem]
    slave_stats: _common_pb2.CharacterCharacteristics
    shortcuts: _containers.RepeatedCompositeFieldContainer[_common_pb2.Shortcut]
    def __init__(self, master_id: _Optional[int] = ..., slave_id: _Optional[int] = ..., slave_turn: _Optional[int] = ..., slave_spells: _Optional[_Iterable[_Union[_common_pb2.SpellItem, _Mapping]]] = ..., slave_stats: _Optional[_Union[_common_pb2.CharacterCharacteristics, _Mapping]] = ..., shortcuts: _Optional[_Iterable[_Union[_common_pb2.Shortcut, _Mapping]]] = ...) -> None: ...

class FightSlaveNoLongerControlledEvent(_message.Message):
    __slots__ = ("master_id", "slave_id")
    MASTER_ID_FIELD_NUMBER: _ClassVar[int]
    SLAVE_ID_FIELD_NUMBER: _ClassVar[int]
    master_id: int
    slave_id: int
    def __init__(self, master_id: _Optional[int] = ..., slave_id: _Optional[int] = ...) -> None: ...

class FightRefreshCharacterStatsEvent(_message.Message):
    __slots__ = ("fighter_id", "stats")
    FIGHTER_ID_FIELD_NUMBER: _ClassVar[int]
    STATS_FIELD_NUMBER: _ClassVar[int]
    fighter_id: int
    stats: _common_pb2.FightCharacteristics
    def __init__(self, fighter_id: _Optional[int] = ..., stats: _Optional[_Union[_common_pb2.FightCharacteristics, _Mapping]] = ...) -> None: ...

class FightIsTurnReadyEvent(_message.Message):
    __slots__ = ("character_id",)
    CHARACTER_ID_FIELD_NUMBER: _ClassVar[int]
    character_id: int
    def __init__(self, character_id: _Optional[int] = ...) -> None: ...

class FightSynchronizeEvent(_message.Message):
    __slots__ = ("fighters",)
    FIGHTERS_FIELD_NUMBER: _ClassVar[int]
    fighters: _containers.RepeatedCompositeFieldContainer[_common_pb2.ActorPositionInformation]
    def __init__(self, fighters: _Optional[_Iterable[_Union[_common_pb2.ActorPositionInformation, _Mapping]]] = ...) -> None: ...

class FightTurnEndEvent(_message.Message):
    __slots__ = ("character_id",)
    CHARACTER_ID_FIELD_NUMBER: _ClassVar[int]
    character_id: int
    def __init__(self, character_id: _Optional[int] = ...) -> None: ...

class FightFighterShowEvent(_message.Message):
    __slots__ = ("information", "static_pose")
    INFORMATION_FIELD_NUMBER: _ClassVar[int]
    STATIC_POSE_FIELD_NUMBER: _ClassVar[int]
    information: _common_pb2.ActorPositionInformation
    static_pose: bool
    def __init__(self, information: _Optional[_Union[_common_pb2.ActorPositionInformation, _Mapping]] = ..., static_pose: bool = ...) -> None: ...

class FightFighterRefreshEvent(_message.Message):
    __slots__ = ("information",)
    INFORMATION_FIELD_NUMBER: _ClassVar[int]
    information: _common_pb2.ActorPositionInformation
    def __init__(self, information: _Optional[_Union[_common_pb2.ActorPositionInformation, _Mapping]] = ...) -> None: ...

class FightChallengeJoinRefuseEvent(_message.Message):
    __slots__ = ("player_id", "reason")
    class FighterRefusedReason(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        FIGHTER_REFUSED: _ClassVar[FightChallengeJoinRefuseEvent.FighterRefusedReason]
        FIGHTER_ACCEPTED: _ClassVar[FightChallengeJoinRefuseEvent.FighterRefusedReason]
        CHALLENGE_FULL: _ClassVar[FightChallengeJoinRefuseEvent.FighterRefusedReason]
        TEAM_FULL: _ClassVar[FightChallengeJoinRefuseEvent.FighterRefusedReason]
        WRONG_ALIGNMENT: _ClassVar[FightChallengeJoinRefuseEvent.FighterRefusedReason]
        WRONG_GUILD: _ClassVar[FightChallengeJoinRefuseEvent.FighterRefusedReason]
        TOO_LATE: _ClassVar[FightChallengeJoinRefuseEvent.FighterRefusedReason]
        MUTANT_REFUSED: _ClassVar[FightChallengeJoinRefuseEvent.FighterRefusedReason]
        WRONG_MAP: _ClassVar[FightChallengeJoinRefuseEvent.FighterRefusedReason]
        JUST_RESPAWNED: _ClassVar[FightChallengeJoinRefuseEvent.FighterRefusedReason]
        IM_OCCUPIED: _ClassVar[FightChallengeJoinRefuseEvent.FighterRefusedReason]
        OPPONENT_OCCUPIED: _ClassVar[FightChallengeJoinRefuseEvent.FighterRefusedReason]
        FIGHT_MYSELF: _ClassVar[FightChallengeJoinRefuseEvent.FighterRefusedReason]
        INSUFFICIENT_RIGHTS: _ClassVar[FightChallengeJoinRefuseEvent.FighterRefusedReason]
        MEMBER_ACCOUNT_NEEDED: _ClassVar[FightChallengeJoinRefuseEvent.FighterRefusedReason]
        OPPONENT_NOT_MEMBER: _ClassVar[FightChallengeJoinRefuseEvent.FighterRefusedReason]
        TEAM_LIMITED_BY_MAIN_CHARACTER: _ClassVar[FightChallengeJoinRefuseEvent.FighterRefusedReason]
        MULTI_ACCOUNT_NOT_ALLOWED: _ClassVar[FightChallengeJoinRefuseEvent.FighterRefusedReason]
        GHOST_REFUSED: _ClassVar[FightChallengeJoinRefuseEvent.FighterRefusedReason]
        WRONG_ALLIANCE: _ClassVar[FightChallengeJoinRefuseEvent.FighterRefusedReason]
        AVA_ZONE: _ClassVar[FightChallengeJoinRefuseEvent.FighterRefusedReason]
        ENTITY_REFUSED: _ClassVar[FightChallengeJoinRefuseEvent.FighterRefusedReason]
        NOT_ENOUGH_ROOM: _ClassVar[FightChallengeJoinRefuseEvent.FighterRefusedReason]
        GUEST_ACCOUNT: _ClassVar[FightChallengeJoinRefuseEvent.FighterRefusedReason]
    FIGHTER_REFUSED: FightChallengeJoinRefuseEvent.FighterRefusedReason
    FIGHTER_ACCEPTED: FightChallengeJoinRefuseEvent.FighterRefusedReason
    CHALLENGE_FULL: FightChallengeJoinRefuseEvent.FighterRefusedReason
    TEAM_FULL: FightChallengeJoinRefuseEvent.FighterRefusedReason
    WRONG_ALIGNMENT: FightChallengeJoinRefuseEvent.FighterRefusedReason
    WRONG_GUILD: FightChallengeJoinRefuseEvent.FighterRefusedReason
    TOO_LATE: FightChallengeJoinRefuseEvent.FighterRefusedReason
    MUTANT_REFUSED: FightChallengeJoinRefuseEvent.FighterRefusedReason
    WRONG_MAP: FightChallengeJoinRefuseEvent.FighterRefusedReason
    JUST_RESPAWNED: FightChallengeJoinRefuseEvent.FighterRefusedReason
    IM_OCCUPIED: FightChallengeJoinRefuseEvent.FighterRefusedReason
    OPPONENT_OCCUPIED: FightChallengeJoinRefuseEvent.FighterRefusedReason
    FIGHT_MYSELF: FightChallengeJoinRefuseEvent.FighterRefusedReason
    INSUFFICIENT_RIGHTS: FightChallengeJoinRefuseEvent.FighterRefusedReason
    MEMBER_ACCOUNT_NEEDED: FightChallengeJoinRefuseEvent.FighterRefusedReason
    OPPONENT_NOT_MEMBER: FightChallengeJoinRefuseEvent.FighterRefusedReason
    TEAM_LIMITED_BY_MAIN_CHARACTER: FightChallengeJoinRefuseEvent.FighterRefusedReason
    MULTI_ACCOUNT_NOT_ALLOWED: FightChallengeJoinRefuseEvent.FighterRefusedReason
    GHOST_REFUSED: FightChallengeJoinRefuseEvent.FighterRefusedReason
    WRONG_ALLIANCE: FightChallengeJoinRefuseEvent.FighterRefusedReason
    AVA_ZONE: FightChallengeJoinRefuseEvent.FighterRefusedReason
    ENTITY_REFUSED: FightChallengeJoinRefuseEvent.FighterRefusedReason
    NOT_ENOUGH_ROOM: FightChallengeJoinRefuseEvent.FighterRefusedReason
    GUEST_ACCOUNT: FightChallengeJoinRefuseEvent.FighterRefusedReason
    PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    player_id: int
    reason: FightChallengeJoinRefuseEvent.FighterRefusedReason
    def __init__(self, player_id: _Optional[int] = ..., reason: _Optional[_Union[FightChallengeJoinRefuseEvent.FighterRefusedReason, str]] = ...) -> None: ...

class FightResume(_message.Message):
    __slots__ = ("spells_cool_down", "summon_count", "bomb_count", "slaves_information")
    SPELLS_COOL_DOWN_FIELD_NUMBER: _ClassVar[int]
    SUMMON_COUNT_FIELD_NUMBER: _ClassVar[int]
    BOMB_COUNT_FIELD_NUMBER: _ClassVar[int]
    SLAVES_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    spells_cool_down: _containers.RepeatedCompositeFieldContainer[_common_pb2.FightSpellCoolDown]
    summon_count: int
    bomb_count: int
    slaves_information: _containers.RepeatedCompositeFieldContainer[_common_pb2.FightResumeSlaves]
    def __init__(self, spells_cool_down: _Optional[_Iterable[_Union[_common_pb2.FightSpellCoolDown, _Mapping]]] = ..., summon_count: _Optional[int] = ..., bomb_count: _Optional[int] = ..., slaves_information: _Optional[_Iterable[_Union[_common_pb2.FightResumeSlaves, _Mapping]]] = ...) -> None: ...

class FightMapInformationResponse(_message.Message):
    __slots__ = ("map_id", "fight_map_id", "fight_start_positions")
    MAP_ID_FIELD_NUMBER: _ClassVar[int]
    FIGHT_MAP_ID_FIELD_NUMBER: _ClassVar[int]
    FIGHT_START_POSITIONS_FIELD_NUMBER: _ClassVar[int]
    map_id: int
    fight_map_id: int
    fight_start_positions: _common_pb2.FightStartingPositions
    def __init__(self, map_id: _Optional[int] = ..., fight_map_id: _Optional[int] = ..., fight_start_positions: _Optional[_Union[_common_pb2.FightStartingPositions, _Mapping]] = ...) -> None: ...
