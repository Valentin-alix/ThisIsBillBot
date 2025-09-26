import common_pb2 as _common_pb2
import spell_pb2 as _spell_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class UnknownOneHundredSixtyOne(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class FightTurnReadyRequest(_message.Message):
    __slots__ = ("is_ready",)
    IS_READY_FIELD_NUMBER: _ClassVar[int]
    is_ready: bool
    def __init__(self, is_ready: bool = ...) -> None: ...

class FightSlaveNoLongerControlledEvent(_message.Message):
    __slots__ = ("master_id", "slave_id")
    MASTER_ID_FIELD_NUMBER: _ClassVar[int]
    SLAVE_ID_FIELD_NUMBER: _ClassVar[int]
    master_id: int
    slave_id: int
    def __init__(self, master_id: _Optional[int] = ..., slave_id: _Optional[int] = ...) -> None: ...

class FightTurnFinishRequest(_message.Message):
    __slots__ = ("is_afk",)
    IS_AFK_FIELD_NUMBER: _ClassVar[int]
    is_afk: bool
    def __init__(self, is_afk: bool = ...) -> None: ...

class FightTurnListEvent(_message.Message):
    __slots__ = ("entries",)
    class Entry(_message.Message):
        __slots__ = ("named_fighter", "indexed_fighter")
        NAMED_FIGHTER_FIELD_NUMBER: _ClassVar[int]
        INDEXED_FIGHTER_FIELD_NUMBER: _ClassVar[int]
        named_fighter: FightTurnListEvent.NamedFighter
        indexed_fighter: FightTurnListEvent.IndexedFighter
        def __init__(self, named_fighter: _Optional[_Union[FightTurnListEvent.NamedFighter, _Mapping]] = ..., indexed_fighter: _Optional[_Union[FightTurnListEvent.IndexedFighter, _Mapping]] = ...) -> None: ...
    class NamedFighter(_message.Message):
        __slots__ = ("name", "fighter_id")
        NAME_FIELD_NUMBER: _ClassVar[int]
        FIGHTER_ID_FIELD_NUMBER: _ClassVar[int]
        name: str
        fighter_id: int
        def __init__(self, name: _Optional[str] = ..., fighter_id: _Optional[int] = ...) -> None: ...
    class IndexedFighter(_message.Message):
        __slots__ = ("fighter_id", "slain", "index")
        FIGHTER_ID_FIELD_NUMBER: _ClassVar[int]
        SLAIN_FIELD_NUMBER: _ClassVar[int]
        INDEX_FIELD_NUMBER: _ClassVar[int]
        fighter_id: int
        slain: bool
        index: int
        def __init__(self, fighter_id: _Optional[int] = ..., slain: bool = ..., index: _Optional[int] = ...) -> None: ...
    class UnknownOneHundredFiftyEight(_message.Message):
        __slots__ = ("unknown_three_hundred_forty", "unknown_three_hundred_forty_one")
        UNKNOWN_THREE_HUNDRED_FORTY_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_THREE_HUNDRED_FORTY_ONE_FIELD_NUMBER: _ClassVar[int]
        unknown_three_hundred_forty: FightTurnListEvent.UnknownOneHundredSixty
        unknown_three_hundred_forty_one: FightTurnListEvent.UnknownOneHundredFiftyNine
        def __init__(self, unknown_three_hundred_forty: _Optional[_Union[FightTurnListEvent.UnknownOneHundredSixty, _Mapping]] = ..., unknown_three_hundred_forty_one: _Optional[_Union[FightTurnListEvent.UnknownOneHundredFiftyNine, _Mapping]] = ...) -> None: ...
    class UnknownOneHundredFiftyNine(_message.Message):
        __slots__ = ("unknown_three_hundred_forty_two", "unknown_three_hundred_forty_three")
        UNKNOWN_THREE_HUNDRED_FORTY_TWO_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_THREE_HUNDRED_FORTY_THREE_FIELD_NUMBER: _ClassVar[int]
        unknown_three_hundred_forty_two: bool
        unknown_three_hundred_forty_three: int
        def __init__(self, unknown_three_hundred_forty_two: bool = ..., unknown_three_hundred_forty_three: _Optional[int] = ...) -> None: ...
    class UnknownOneHundredSixty(_message.Message):
        __slots__ = ("unknown_three_hundred_forty_four", "unknown_three_hundred_forty_five")
        UNKNOWN_THREE_HUNDRED_FORTY_FOUR_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_THREE_HUNDRED_FORTY_FIVE_FIELD_NUMBER: _ClassVar[int]
        unknown_three_hundred_forty_four: int
        unknown_three_hundred_forty_five: str
        def __init__(self, unknown_three_hundred_forty_four: _Optional[int] = ..., unknown_three_hundred_forty_five: _Optional[str] = ...) -> None: ...
    ENTRIES_FIELD_NUMBER: _ClassVar[int]
    entries: _containers.RepeatedCompositeFieldContainer[RefreshCooldownEvent.CooldownContext.Entry]
    def __init__(self, entries: _Optional[_Iterable[_Union[RefreshCooldownEvent.CooldownContext.Entry, _Mapping]]] = ...) -> None: ...

class FightEffectsEvent(_message.Message):
    __slots__ = ("effect",)
    EFFECT_FIELD_NUMBER: _ClassVar[int]
    effect: _common_pb2.FightRemovableEffectExtendedInformation
    def __init__(self, effect: _Optional[_Union[_common_pb2.FightRemovableEffectExtendedInformation, _Mapping]] = ...) -> None: ...

class FightChangeControllerEvent(_message.Message):
    __slots__ = ("efvm", "efvo", "efvp")
    EFVM_FIELD_NUMBER: _ClassVar[int]
    EFVO_FIELD_NUMBER: _ClassVar[int]
    EFVP_FIELD_NUMBER: _ClassVar[int]
    efvm: int
    efvo: bool
    efvp: int
    def __init__(self, efvm: _Optional[int] = ..., efvo: bool = ..., efvp: _Optional[int] = ...) -> None: ...

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
    __slots__ = ("stat_resume", "stat_detailed")
    class StatDetailedEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: DetailedStatistics
        def __init__(self, key: _Optional[int] = ..., value: _Optional[_Union[DetailedStatistics, _Mapping]] = ...) -> None: ...
    STAT_RESUME_FIELD_NUMBER: _ClassVar[int]
    STAT_DETAILED_FIELD_NUMBER: _ClassVar[int]
    stat_resume: BaseStatistics
    stat_detailed: _containers.MessageMap[int, DetailedStatistics]
    def __init__(self, stat_resume: _Optional[_Union[BaseStatistics, _Mapping]] = ..., stat_detailed: _Optional[_Mapping[int, DetailedStatistics]] = ...) -> None: ...

class FightNewRoundEvent(_message.Message):
    __slots__ = ("round_number",)
    ROUND_NUMBER_FIELD_NUMBER: _ClassVar[int]
    round_number: int
    def __init__(self, round_number: _Optional[int] = ...) -> None: ...

class FightTurnEvent(_message.Message):
    __slots__ = ("character_id", "base_time", "extra_time", "remaining_time", "unknown_three_hundred_thirty_eight", "unknown_three_hundred_thirty_nine")
    CHARACTER_ID_FIELD_NUMBER: _ClassVar[int]
    BASE_TIME_FIELD_NUMBER: _ClassVar[int]
    EXTRA_TIME_FIELD_NUMBER: _ClassVar[int]
    REMAINING_TIME_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_THREE_HUNDRED_THIRTY_EIGHT_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_THREE_HUNDRED_THIRTY_NINE_FIELD_NUMBER: _ClassVar[int]
    character_id: int
    base_time: int
    extra_time: int
    remaining_time: int
    unknown_three_hundred_thirty_eight: int
    unknown_three_hundred_thirty_nine: int
    def __init__(self, character_id: _Optional[int] = ..., base_time: _Optional[int] = ..., extra_time: _Optional[int] = ..., remaining_time: _Optional[int] = ..., unknown_three_hundred_thirty_eight: _Optional[int] = ..., unknown_three_hundred_thirty_nine: _Optional[int] = ...) -> None: ...

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

class TimelineRefreshEvent(_message.Message):
    __slots__ = ("eftc",)
    class ios(_message.Message):
        __slots__ = ("efsx", "efsy")
        EFSX_FIELD_NUMBER: _ClassVar[int]
        EFSY_FIELD_NUMBER: _ClassVar[int]
        efsx: bool
        efsy: int
        def __init__(self, efsx: bool = ..., efsy: _Optional[int] = ...) -> None: ...
    EFTC_FIELD_NUMBER: _ClassVar[int]
    eftc: _containers.RepeatedCompositeFieldContainer[TimelineRefreshEvent.ios]
    def __init__(self, eftc: _Optional[_Iterable[_Union[TimelineRefreshEvent.ios, _Mapping]]] = ...) -> None: ...

class FightSlaveSwitchContextEvent(_message.Message):
    __slots__ = ("master_id", "context_entries", "shortcuts", "slave_spells", "spell_modifiers", "slave_id")
    class ContextEntry(_message.Message):
        __slots__ = ("type", "enabled", "value", "action_type", "modifier_type")
        class ContextEntryType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            CONTEXT_ENTRY_TYPE_0: _ClassVar[FightSlaveSwitchContextEvent.ContextEntry.ContextEntryType]
            CONTEXT_ENTRY_TYPE_1: _ClassVar[FightSlaveSwitchContextEvent.ContextEntry.ContextEntryType]
            CONTEXT_ENTRY_TYPE_2: _ClassVar[FightSlaveSwitchContextEvent.ContextEntry.ContextEntryType]
            CONTEXT_ENTRY_TYPE_3: _ClassVar[FightSlaveSwitchContextEvent.ContextEntry.ContextEntryType]
            CONTEXT_ENTRY_TYPE_4: _ClassVar[FightSlaveSwitchContextEvent.ContextEntry.ContextEntryType]
            CONTEXT_ENTRY_TYPE_5: _ClassVar[FightSlaveSwitchContextEvent.ContextEntry.ContextEntryType]
            CONTEXT_ENTRY_TYPE_6: _ClassVar[FightSlaveSwitchContextEvent.ContextEntry.ContextEntryType]
            CONTEXT_ENTRY_TYPE_7: _ClassVar[FightSlaveSwitchContextEvent.ContextEntry.ContextEntryType]
            CONTEXT_ENTRY_TYPE_8: _ClassVar[FightSlaveSwitchContextEvent.ContextEntry.ContextEntryType]
        CONTEXT_ENTRY_TYPE_0: FightSlaveSwitchContextEvent.ContextEntry.ContextEntryType
        CONTEXT_ENTRY_TYPE_1: FightSlaveSwitchContextEvent.ContextEntry.ContextEntryType
        CONTEXT_ENTRY_TYPE_2: FightSlaveSwitchContextEvent.ContextEntry.ContextEntryType
        CONTEXT_ENTRY_TYPE_3: FightSlaveSwitchContextEvent.ContextEntry.ContextEntryType
        CONTEXT_ENTRY_TYPE_4: FightSlaveSwitchContextEvent.ContextEntry.ContextEntryType
        CONTEXT_ENTRY_TYPE_5: FightSlaveSwitchContextEvent.ContextEntry.ContextEntryType
        CONTEXT_ENTRY_TYPE_6: FightSlaveSwitchContextEvent.ContextEntry.ContextEntryType
        CONTEXT_ENTRY_TYPE_7: FightSlaveSwitchContextEvent.ContextEntry.ContextEntryType
        CONTEXT_ENTRY_TYPE_8: FightSlaveSwitchContextEvent.ContextEntry.ContextEntryType
        TYPE_FIELD_NUMBER: _ClassVar[int]
        ENABLED_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        ACTION_TYPE_FIELD_NUMBER: _ClassVar[int]
        MODIFIER_TYPE_FIELD_NUMBER: _ClassVar[int]
        type: FightSlaveSwitchContextEvent.ContextEntry.ContextEntryType
        enabled: bool
        value: int
        action_type: _common_pb2.SpellModifierActionType
        modifier_type: _common_pb2.SpellModifierType
        def __init__(self, type: _Optional[_Union[FightSlaveSwitchContextEvent.ContextEntry.ContextEntryType, str]] = ..., enabled: bool = ..., value: _Optional[int] = ..., action_type: _Optional[_Union[_common_pb2.SpellModifierActionType, str]] = ..., modifier_type: _Optional[_Union[_common_pb2.SpellModifierType, str]] = ...) -> None: ...
    MASTER_ID_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_ENTRIES_FIELD_NUMBER: _ClassVar[int]
    SHORTCUTS_FIELD_NUMBER: _ClassVar[int]
    SLAVE_SPELLS_FIELD_NUMBER: _ClassVar[int]
    SPELL_MODIFIERS_FIELD_NUMBER: _ClassVar[int]
    SLAVE_ID_FIELD_NUMBER: _ClassVar[int]
    master_id: int
    context_entries: _containers.RepeatedCompositeFieldContainer[FightSlaveSwitchContextEvent.ContextEntry]
    shortcuts: _containers.RepeatedCompositeFieldContainer[_common_pb2.Shortcut]
    slave_spells: _containers.RepeatedCompositeFieldContainer[_spell_pb2.SpellItem]
    spell_modifiers: _containers.RepeatedCompositeFieldContainer[_common_pb2.SpellModifier]
    slave_id: int
    def __init__(self, master_id: _Optional[int] = ..., context_entries: _Optional[_Iterable[_Union[FightSlaveSwitchContextEvent.ContextEntry, _Mapping]]] = ..., shortcuts: _Optional[_Iterable[_Union[_common_pb2.Shortcut, _Mapping]]] = ..., slave_spells: _Optional[_Iterable[_Union[_spell_pb2.SpellItem, _Mapping]]] = ..., spell_modifiers: _Optional[_Iterable[_Union[_common_pb2.SpellModifier, _Mapping]]] = ..., slave_id: _Optional[int] = ...) -> None: ...

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

class RefreshCooldownEvent(_message.Message):
    __slots__ = ("character_id", "first_contexts", "second_contexts", "spell_cool_downs")
    class CooldownContext(_message.Message):
        __slots__ = ("entries", "value", "type", "count")
        class CooldownContextType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            COOLDOWN_CONTEXT_TYPE_0: _ClassVar[RefreshCooldownEvent.CooldownContext.CooldownContextType]
            COOLDOWN_CONTEXT_TYPE_1: _ClassVar[RefreshCooldownEvent.CooldownContext.CooldownContextType]
            COOLDOWN_CONTEXT_TYPE_2: _ClassVar[RefreshCooldownEvent.CooldownContext.CooldownContextType]
            COOLDOWN_CONTEXT_TYPE_3: _ClassVar[RefreshCooldownEvent.CooldownContext.CooldownContextType]
            COOLDOWN_CONTEXT_TYPE_4: _ClassVar[RefreshCooldownEvent.CooldownContext.CooldownContextType]
            COOLDOWN_CONTEXT_TYPE_5: _ClassVar[RefreshCooldownEvent.CooldownContext.CooldownContextType]
            COOLDOWN_CONTEXT_TYPE_6: _ClassVar[RefreshCooldownEvent.CooldownContext.CooldownContextType]
            COOLDOWN_CONTEXT_TYPE_7: _ClassVar[RefreshCooldownEvent.CooldownContext.CooldownContextType]
        COOLDOWN_CONTEXT_TYPE_0: RefreshCooldownEvent.CooldownContext.CooldownContextType
        COOLDOWN_CONTEXT_TYPE_1: RefreshCooldownEvent.CooldownContext.CooldownContextType
        COOLDOWN_CONTEXT_TYPE_2: RefreshCooldownEvent.CooldownContext.CooldownContextType
        COOLDOWN_CONTEXT_TYPE_3: RefreshCooldownEvent.CooldownContext.CooldownContextType
        COOLDOWN_CONTEXT_TYPE_4: RefreshCooldownEvent.CooldownContext.CooldownContextType
        COOLDOWN_CONTEXT_TYPE_5: RefreshCooldownEvent.CooldownContext.CooldownContextType
        COOLDOWN_CONTEXT_TYPE_6: RefreshCooldownEvent.CooldownContext.CooldownContextType
        COOLDOWN_CONTEXT_TYPE_7: RefreshCooldownEvent.CooldownContext.CooldownContextType
        class Entry(_message.Message):
            __slots__ = ("first_id", "second_id", "value")
            FIRST_ID_FIELD_NUMBER: _ClassVar[int]
            SECOND_ID_FIELD_NUMBER: _ClassVar[int]
            VALUE_FIELD_NUMBER: _ClassVar[int]
            first_id: int
            second_id: int
            value: int
            def __init__(self, first_id: _Optional[int] = ..., second_id: _Optional[int] = ..., value: _Optional[int] = ...) -> None: ...
        ENTRIES_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        TYPE_FIELD_NUMBER: _ClassVar[int]
        COUNT_FIELD_NUMBER: _ClassVar[int]
        entries: _containers.RepeatedCompositeFieldContainer[RefreshCooldownEvent.CooldownContext.Entry]
        value: int
        type: RefreshCooldownEvent.CooldownContext.CooldownContextType
        count: int
        def __init__(self, entries: _Optional[_Iterable[_Union[RefreshCooldownEvent.CooldownContext.Entry, _Mapping]]] = ..., value: _Optional[int] = ..., type: _Optional[_Union[RefreshCooldownEvent.CooldownContext.CooldownContextType, str]] = ..., count: _Optional[int] = ...) -> None: ...
    CHARACTER_ID_FIELD_NUMBER: _ClassVar[int]
    FIRST_CONTEXTS_FIELD_NUMBER: _ClassVar[int]
    SECOND_CONTEXTS_FIELD_NUMBER: _ClassVar[int]
    SPELL_COOL_DOWNS_FIELD_NUMBER: _ClassVar[int]
    character_id: int
    first_contexts: _containers.RepeatedCompositeFieldContainer[RefreshCooldownEvent.CooldownContext]
    second_contexts: _containers.RepeatedCompositeFieldContainer[RefreshCooldownEvent.CooldownContext]
    spell_cool_downs: _containers.RepeatedCompositeFieldContainer[_common_pb2.FightSpellCoolDown]
    def __init__(self, character_id: _Optional[int] = ..., first_contexts: _Optional[_Iterable[_Union[RefreshCooldownEvent.CooldownContext, _Mapping]]] = ..., second_contexts: _Optional[_Iterable[_Union[RefreshCooldownEvent.CooldownContext, _Mapping]]] = ..., spell_cool_downs: _Optional[_Iterable[_Union[_common_pb2.FightSpellCoolDown, _Mapping]]] = ...) -> None: ...

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
    __slots__ = ("fighter_resume_infos", "slaves_information")
    FIGHTER_RESUME_INFOS_FIELD_NUMBER: _ClassVar[int]
    SLAVES_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    fighter_resume_infos: _containers.RepeatedCompositeFieldContainer[FighterResumeInfo]
    slaves_information: _containers.RepeatedCompositeFieldContainer[_common_pb2.FightResumeSlaves]
    def __init__(self, fighter_resume_infos: _Optional[_Iterable[_Union[FighterResumeInfo, _Mapping]]] = ..., slaves_information: _Optional[_Iterable[_Union[_common_pb2.FightResumeSlaves, _Mapping]]] = ...) -> None: ...

class FighterResumeInfo(_message.Message):
    __slots__ = ("efzz", "egaa", "egab", "spells_cool_down", "fight_spell_cast")
    EFZZ_FIELD_NUMBER: _ClassVar[int]
    EGAA_FIELD_NUMBER: _ClassVar[int]
    EGAB_FIELD_NUMBER: _ClassVar[int]
    SPELLS_COOL_DOWN_FIELD_NUMBER: _ClassVar[int]
    FIGHT_SPELL_CAST_FIELD_NUMBER: _ClassVar[int]
    efzz: int
    egaa: int
    egab: int
    spells_cool_down: _containers.RepeatedCompositeFieldContainer[_common_pb2.FightSpellCoolDown]
    fight_spell_cast: _containers.RepeatedCompositeFieldContainer[FightSpellCast]
    def __init__(self, efzz: _Optional[int] = ..., egaa: _Optional[int] = ..., egab: _Optional[int] = ..., spells_cool_down: _Optional[_Iterable[_Union[_common_pb2.FightSpellCoolDown, _Mapping]]] = ..., fight_spell_cast: _Optional[_Iterable[_Union[FightSpellCast, _Mapping]]] = ...) -> None: ...

class FightSpellCast(_message.Message):
    __slots__ = ("ejrs", "ejrt", "cast_count_one_someone")
    EJRS_FIELD_NUMBER: _ClassVar[int]
    EJRT_FIELD_NUMBER: _ClassVar[int]
    CAST_COUNT_ONE_SOMEONE_FIELD_NUMBER: _ClassVar[int]
    ejrs: int
    ejrt: int
    cast_count_one_someone: _containers.RepeatedCompositeFieldContainer[CastCountOneSomeone]
    def __init__(self, ejrs: _Optional[int] = ..., ejrt: _Optional[int] = ..., cast_count_one_someone: _Optional[_Iterable[_Union[CastCountOneSomeone, _Mapping]]] = ...) -> None: ...

class CastCountOneSomeone(_message.Message):
    __slots__ = ("ejrn", "ejro")
    EJRN_FIELD_NUMBER: _ClassVar[int]
    EJRO_FIELD_NUMBER: _ClassVar[int]
    ejrn: int
    ejro: int
    def __init__(self, ejrn: _Optional[int] = ..., ejro: _Optional[int] = ...) -> None: ...

class FightMapInformationResponse(_message.Message):
    __slots__ = ("map_id", "fight_map_id", "fight_start_positions")
    MAP_ID_FIELD_NUMBER: _ClassVar[int]
    FIGHT_MAP_ID_FIELD_NUMBER: _ClassVar[int]
    FIGHT_START_POSITIONS_FIELD_NUMBER: _ClassVar[int]
    map_id: int
    fight_map_id: int
    fight_start_positions: _common_pb2.FightStartingPositions
    def __init__(self, map_id: _Optional[int] = ..., fight_map_id: _Optional[int] = ..., fight_start_positions: _Optional[_Union[_common_pb2.FightStartingPositions, _Mapping]] = ...) -> None: ...

class FightLiveStateEvent(_message.Message):
    __slots__ = ("entities_states",)
    class FightEntityState(_message.Message):
        __slots__ = ("entity_id", "is_dead")
        ENTITY_ID_FIELD_NUMBER: _ClassVar[int]
        IS_DEAD_FIELD_NUMBER: _ClassVar[int]
        entity_id: int
        is_dead: bool
        def __init__(self, entity_id: _Optional[int] = ..., is_dead: bool = ...) -> None: ...
    ENTITIES_STATES_FIELD_NUMBER: _ClassVar[int]
    entities_states: _containers.RepeatedCompositeFieldContainer[FightLiveStateEvent.FightEntityState]
    def __init__(self, entities_states: _Optional[_Iterable[_Union[FightLiveStateEvent.FightEntityState, _Mapping]]] = ...) -> None: ...

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

class UnknownOneHundredSixtyTwo(_message.Message):
    __slots__ = ("unknown_three_hundred_forty_six", "unknown_three_hundred_forty_seven")
    UNKNOWN_THREE_HUNDRED_FORTY_SIX_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_THREE_HUNDRED_FORTY_SEVEN_FIELD_NUMBER: _ClassVar[int]
    unknown_three_hundred_forty_six: int
    unknown_three_hundred_forty_seven: _common_pb2.UnknownOneHundredTwentyOne
    def __init__(self, unknown_three_hundred_forty_six: _Optional[int] = ..., unknown_three_hundred_forty_seven: _Optional[_Union[_common_pb2.UnknownOneHundredTwentyOne, _Mapping]] = ...) -> None: ...

class UnknownOneHundredSixtyThree(_message.Message):
    __slots__ = ("unknown_three_hundred_forty_eight", "unknown_three_hundred_forty_nine", "unknown_three_hundred_fifty")
    UNKNOWN_THREE_HUNDRED_FORTY_EIGHT_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_THREE_HUNDRED_FORTY_NINE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_THREE_HUNDRED_FIFTY_FIELD_NUMBER: _ClassVar[int]
    unknown_three_hundred_forty_eight: _containers.RepeatedCompositeFieldContainer[_common_pb2.Shortcut]
    unknown_three_hundred_forty_nine: int
    unknown_three_hundred_fifty: _containers.RepeatedCompositeFieldContainer[_spell_pb2.SpellItem]
    def __init__(self, unknown_three_hundred_forty_eight: _Optional[_Iterable[_Union[_common_pb2.Shortcut, _Mapping]]] = ..., unknown_three_hundred_forty_nine: _Optional[int] = ..., unknown_three_hundred_fifty: _Optional[_Iterable[_Union[_spell_pb2.SpellItem, _Mapping]]] = ...) -> None: ...

class UnknownOneHundredSixtyFour(_message.Message):
    __slots__ = ("unknown_three_hundred_fifty_one", "unknown_three_hundred_fifty_two")
    UNKNOWN_THREE_HUNDRED_FIFTY_ONE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_THREE_HUNDRED_FIFTY_TWO_FIELD_NUMBER: _ClassVar[int]
    unknown_three_hundred_fifty_one: int
    unknown_three_hundred_fifty_two: _common_pb2.UnknownOneHundredTwentyOne
    def __init__(self, unknown_three_hundred_fifty_one: _Optional[int] = ..., unknown_three_hundred_fifty_two: _Optional[_Union[_common_pb2.UnknownOneHundredTwentyOne, _Mapping]] = ...) -> None: ...

class UnknownOneHundredSixtyFive(_message.Message):
    __slots__ = ("unknown_three_hundred_fifty_three",)
    UNKNOWN_THREE_HUNDRED_FIFTY_THREE_FIELD_NUMBER: _ClassVar[int]
    unknown_three_hundred_fifty_three: bool
    def __init__(self, unknown_three_hundred_fifty_three: bool = ...) -> None: ...

class UnknownOneHundredSixtySix(_message.Message):
    __slots__ = ("unknown_three_hundred_fifty_four", "unknown_three_hundred_fifty_five")
    UNKNOWN_THREE_HUNDRED_FIFTY_FOUR_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_THREE_HUNDRED_FIFTY_FIVE_FIELD_NUMBER: _ClassVar[int]
    unknown_three_hundred_fifty_four: int
    unknown_three_hundred_fifty_five: int
    def __init__(self, unknown_three_hundred_fifty_four: _Optional[int] = ..., unknown_three_hundred_fifty_five: _Optional[int] = ...) -> None: ...

class UnknownOneHundredSixtySeven(_message.Message):
    __slots__ = ("unknown_three_hundred_fifty_six",)
    UNKNOWN_THREE_HUNDRED_FIFTY_SIX_FIELD_NUMBER: _ClassVar[int]
    unknown_three_hundred_fifty_six: _containers.RepeatedCompositeFieldContainer[UnknownOneHundredSixtyOne]
    def __init__(self, unknown_three_hundred_fifty_six: _Optional[_Iterable[_Union[UnknownOneHundredSixtyOne, _Mapping]]] = ...) -> None: ...

class UnknownOneHundredSixtyEight(_message.Message):
    __slots__ = ("unknown_three_hundred_fifty_seven",)
    UNKNOWN_THREE_HUNDRED_FIFTY_SEVEN_FIELD_NUMBER: _ClassVar[int]
    unknown_three_hundred_fifty_seven: int
    def __init__(self, unknown_three_hundred_fifty_seven: _Optional[int] = ...) -> None: ...

class UnknownOneHundredSixtyNine(_message.Message):
    __slots__ = ("unknown_three_hundred_fifty_eight", "unknown_three_hundred_fifty_nine", "unknown_three_hundred_sixty")
    UNKNOWN_THREE_HUNDRED_FIFTY_EIGHT_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_THREE_HUNDRED_FIFTY_NINE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_THREE_HUNDRED_SIXTY_FIELD_NUMBER: _ClassVar[int]
    unknown_three_hundred_fifty_eight: int
    unknown_three_hundred_fifty_nine: int
    unknown_three_hundred_sixty: int
    def __init__(self, unknown_three_hundred_fifty_eight: _Optional[int] = ..., unknown_three_hundred_fifty_nine: _Optional[int] = ..., unknown_three_hundred_sixty: _Optional[int] = ...) -> None: ...
