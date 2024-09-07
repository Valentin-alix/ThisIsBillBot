from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ArenaType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ONE_VS_ONE: _ClassVar[ArenaType]
    TWO_VS_TWO: _ClassVar[ArenaType]
    THREE_VS_THREE: _ClassVar[ArenaType]
ONE_VS_ONE: ArenaType
TWO_VS_TWO: ArenaType
THREE_VS_THREE: ArenaType

class ArenaRegisterRequest(_message.Message):
    __slots__ = ("arena_type",)
    ARENA_TYPE_FIELD_NUMBER: _ClassVar[int]
    arena_type: ArenaType
    def __init__(self, arena_type: _Optional[_Union[ArenaType, str]] = ...) -> None: ...

class ArenaUnregisterRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ArenaFightAnswerRequest(_message.Message):
    __slots__ = ("accept",)
    ACCEPT_FIELD_NUMBER: _ClassVar[int]
    accept: bool
    def __init__(self, accept: bool = ...) -> None: ...

class ArenaFightAnswerResponse(_message.Message):
    __slots__ = ("acknowledged",)
    ACKNOWLEDGED_FIELD_NUMBER: _ClassVar[int]
    acknowledged: bool
    def __init__(self, acknowledged: bool = ...) -> None: ...

class ArenaRegistrationStatusEvent(_message.Message):
    __slots__ = ("registered", "step", "battle_mode")
    class Step(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        REGISTERED: _ClassVar[ArenaRegistrationStatusEvent.Step]
        WAITING_FIGHT: _ClassVar[ArenaRegistrationStatusEvent.Step]
        STARTING_FIGHT: _ClassVar[ArenaRegistrationStatusEvent.Step]
        UNREGISTERED: _ClassVar[ArenaRegistrationStatusEvent.Step]
    REGISTERED: ArenaRegistrationStatusEvent.Step
    WAITING_FIGHT: ArenaRegistrationStatusEvent.Step
    STARTING_FIGHT: ArenaRegistrationStatusEvent.Step
    UNREGISTERED: ArenaRegistrationStatusEvent.Step
    REGISTERED_FIELD_NUMBER: _ClassVar[int]
    STEP_FIELD_NUMBER: _ClassVar[int]
    BATTLE_MODE_FIELD_NUMBER: _ClassVar[int]
    registered: bool
    step: ArenaRegistrationStatusEvent.Step
    battle_mode: ArenaType
    def __init__(self, registered: bool = ..., step: _Optional[_Union[ArenaRegistrationStatusEvent.Step, str]] = ..., battle_mode: _Optional[_Union[ArenaType, str]] = ...) -> None: ...

class ArenaFightPropositionEvent(_message.Message):
    __slots__ = ("fight_id", "allies", "duration")
    FIGHT_ID_FIELD_NUMBER: _ClassVar[int]
    ALLIES_FIELD_NUMBER: _ClassVar[int]
    DURATION_FIELD_NUMBER: _ClassVar[int]
    fight_id: int
    allies: _containers.RepeatedScalarFieldContainer[int]
    duration: int
    def __init__(self, fight_id: _Optional[int] = ..., allies: _Optional[_Iterable[int]] = ..., duration: _Optional[int] = ...) -> None: ...

class ArenaFighterStatusEvent(_message.Message):
    __slots__ = ("fight_id", "character_id", "accepted")
    FIGHT_ID_FIELD_NUMBER: _ClassVar[int]
    CHARACTER_ID_FIELD_NUMBER: _ClassVar[int]
    ACCEPTED_FIELD_NUMBER: _ClassVar[int]
    fight_id: int
    character_id: int
    accepted: bool
    def __init__(self, fight_id: _Optional[int] = ..., character_id: _Optional[int] = ..., accepted: bool = ...) -> None: ...

class ArenaUpdatePlayerInformationEvent(_message.Message):
    __slots__ = ("arena_ranks", "ban_end_date")
    class ArenaRank(_message.Message):
        __slots__ = ("arena_type", "league_ranking", "best_league_id", "best_rating", "daily_victory_count", "season_victory_count", "daily_fight_count", "season_fight_count", "fight_needed_for_ladder")
        class LeagueRanking(_message.Message):
            __slots__ = ("rating", "league_id", "ladder_position")
            RATING_FIELD_NUMBER: _ClassVar[int]
            LEAGUE_ID_FIELD_NUMBER: _ClassVar[int]
            LADDER_POSITION_FIELD_NUMBER: _ClassVar[int]
            rating: int
            league_id: int
            ladder_position: int
            def __init__(self, rating: _Optional[int] = ..., league_id: _Optional[int] = ..., ladder_position: _Optional[int] = ...) -> None: ...
        ARENA_TYPE_FIELD_NUMBER: _ClassVar[int]
        LEAGUE_RANKING_FIELD_NUMBER: _ClassVar[int]
        BEST_LEAGUE_ID_FIELD_NUMBER: _ClassVar[int]
        BEST_RATING_FIELD_NUMBER: _ClassVar[int]
        DAILY_VICTORY_COUNT_FIELD_NUMBER: _ClassVar[int]
        SEASON_VICTORY_COUNT_FIELD_NUMBER: _ClassVar[int]
        DAILY_FIGHT_COUNT_FIELD_NUMBER: _ClassVar[int]
        SEASON_FIGHT_COUNT_FIELD_NUMBER: _ClassVar[int]
        FIGHT_NEEDED_FOR_LADDER_FIELD_NUMBER: _ClassVar[int]
        arena_type: ArenaType
        league_ranking: ArenaUpdatePlayerInformationEvent.ArenaRank.LeagueRanking
        best_league_id: int
        best_rating: int
        daily_victory_count: int
        season_victory_count: int
        daily_fight_count: int
        season_fight_count: int
        fight_needed_for_ladder: int
        def __init__(self, arena_type: _Optional[_Union[ArenaType, str]] = ..., league_ranking: _Optional[_Union[ArenaUpdatePlayerInformationEvent.ArenaRank.LeagueRanking, _Mapping]] = ..., best_league_id: _Optional[int] = ..., best_rating: _Optional[int] = ..., daily_victory_count: _Optional[int] = ..., season_victory_count: _Optional[int] = ..., daily_fight_count: _Optional[int] = ..., season_fight_count: _Optional[int] = ..., fight_needed_for_ladder: _Optional[int] = ...) -> None: ...
    ARENA_RANKS_FIELD_NUMBER: _ClassVar[int]
    BAN_END_DATE_FIELD_NUMBER: _ClassVar[int]
    arena_ranks: _containers.RepeatedCompositeFieldContainer[ArenaUpdatePlayerInformationEvent.ArenaRank]
    ban_end_date: str
    def __init__(self, arena_ranks: _Optional[_Iterable[_Union[ArenaUpdatePlayerInformationEvent.ArenaRank, _Mapping]]] = ..., ban_end_date: _Optional[str] = ...) -> None: ...

class ArenaSwitchToFightServerEvent(_message.Message):
    __slots__ = ("address", "ports", "token")
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    PORTS_FIELD_NUMBER: _ClassVar[int]
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    address: str
    ports: _containers.RepeatedScalarFieldContainer[int]
    token: str
    def __init__(self, address: _Optional[str] = ..., ports: _Optional[_Iterable[int]] = ..., token: _Optional[str] = ...) -> None: ...

class ArenaLeagueRewardsEvent(_message.Message):
    __slots__ = ("season_id", "league_id", "ladder_position", "end_season_reward")
    SEASON_ID_FIELD_NUMBER: _ClassVar[int]
    LEAGUE_ID_FIELD_NUMBER: _ClassVar[int]
    LADDER_POSITION_FIELD_NUMBER: _ClassVar[int]
    END_SEASON_REWARD_FIELD_NUMBER: _ClassVar[int]
    season_id: int
    league_id: int
    ladder_position: int
    end_season_reward: bool
    def __init__(self, season_id: _Optional[int] = ..., league_id: _Optional[int] = ..., ladder_position: _Optional[int] = ..., end_season_reward: bool = ...) -> None: ...

class ArenaPlayerBehavioursEvent(_message.Message):
    __slots__ = ("flags", "sanctions", "ban_duration")
    FLAGS_FIELD_NUMBER: _ClassVar[int]
    SANCTIONS_FIELD_NUMBER: _ClassVar[int]
    BAN_DURATION_FIELD_NUMBER: _ClassVar[int]
    flags: _containers.RepeatedScalarFieldContainer[str]
    sanctions: _containers.RepeatedScalarFieldContainer[str]
    ban_duration: int
    def __init__(self, flags: _Optional[_Iterable[str]] = ..., sanctions: _Optional[_Iterable[str]] = ..., ban_duration: _Optional[int] = ...) -> None: ...

class ArenaRegistrationWarningEvent(_message.Message):
    __slots__ = ("battle_mode",)
    BATTLE_MODE_FIELD_NUMBER: _ClassVar[int]
    battle_mode: ArenaType
    def __init__(self, battle_mode: _Optional[_Union[ArenaType, str]] = ...) -> None: ...

class ArenaFighterIdleEvent(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ArenaSwitchXpRewardsModeRequest(_message.Message):
    __slots__ = ("xpRewards",)
    XPREWARDS_FIELD_NUMBER: _ClassVar[int]
    xpRewards: bool
    def __init__(self, xpRewards: bool = ...) -> None: ...

class SurrenderStateEvent(_message.Message):
    __slots__ = ("permitSurrender", "permitVote")
    PERMITSURRENDER_FIELD_NUMBER: _ClassVar[int]
    PERMITVOTE_FIELD_NUMBER: _ClassVar[int]
    permitSurrender: bool
    permitVote: bool
    def __init__(self, permitSurrender: bool = ..., permitVote: bool = ...) -> None: ...

class SurrenderInfoRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SurrenderInfoResponse(_message.Message):
    __slots__ = ("surrender_response", "surrender_vote_response", "has_sanction")
    class SurrenderResponse(_message.Message):
        __slots__ = ("accepted", "refused", "before_turn", "before_vote")
        class SurrenderAccepted(_message.Message):
            __slots__ = ()
            def __init__(self) -> None: ...
        class SurrenderRefused(_message.Message):
            __slots__ = ()
            def __init__(self) -> None: ...
        class SurrenderBeforeTurn(_message.Message):
            __slots__ = ("min_turn_for_surrender",)
            MIN_TURN_FOR_SURRENDER_FIELD_NUMBER: _ClassVar[int]
            min_turn_for_surrender: int
            def __init__(self, min_turn_for_surrender: _Optional[int] = ...) -> None: ...
        class SurrenderBeforeVote(_message.Message):
            __slots__ = ()
            def __init__(self) -> None: ...
        ACCEPTED_FIELD_NUMBER: _ClassVar[int]
        REFUSED_FIELD_NUMBER: _ClassVar[int]
        BEFORE_TURN_FIELD_NUMBER: _ClassVar[int]
        BEFORE_VOTE_FIELD_NUMBER: _ClassVar[int]
        accepted: SurrenderInfoResponse.SurrenderResponse.SurrenderAccepted
        refused: SurrenderInfoResponse.SurrenderResponse.SurrenderRefused
        before_turn: SurrenderInfoResponse.SurrenderResponse.SurrenderBeforeTurn
        before_vote: SurrenderInfoResponse.SurrenderResponse.SurrenderBeforeVote
        def __init__(self, accepted: _Optional[_Union[SurrenderInfoResponse.SurrenderResponse.SurrenderAccepted, _Mapping]] = ..., refused: _Optional[_Union[SurrenderInfoResponse.SurrenderResponse.SurrenderRefused, _Mapping]] = ..., before_turn: _Optional[_Union[SurrenderInfoResponse.SurrenderResponse.SurrenderBeforeTurn, _Mapping]] = ..., before_vote: _Optional[_Union[SurrenderInfoResponse.SurrenderResponse.SurrenderBeforeVote, _Mapping]] = ...) -> None: ...
    class SurrenderVoteResponse(_message.Message):
        __slots__ = ("accepted", "refused", "before_turn", "already_asked", "waiting")
        class SurrenderVoteAccepted(_message.Message):
            __slots__ = ()
            def __init__(self) -> None: ...
        class SurrenderVoteRefused(_message.Message):
            __slots__ = ()
            def __init__(self) -> None: ...
        class SurrenderVoteBeforeTurn(_message.Message):
            __slots__ = ("min_turn_for_surrender_vote",)
            MIN_TURN_FOR_SURRENDER_VOTE_FIELD_NUMBER: _ClassVar[int]
            min_turn_for_surrender_vote: int
            def __init__(self, min_turn_for_surrender_vote: _Optional[int] = ...) -> None: ...
        class SurrenderVoteAlreadyAsked(_message.Message):
            __slots__ = ()
            def __init__(self) -> None: ...
        class SurrenderVoteWaiting(_message.Message):
            __slots__ = ("vote_unlock_time_stamp",)
            VOTE_UNLOCK_TIME_STAMP_FIELD_NUMBER: _ClassVar[int]
            vote_unlock_time_stamp: str
            def __init__(self, vote_unlock_time_stamp: _Optional[str] = ...) -> None: ...
        ACCEPTED_FIELD_NUMBER: _ClassVar[int]
        REFUSED_FIELD_NUMBER: _ClassVar[int]
        BEFORE_TURN_FIELD_NUMBER: _ClassVar[int]
        ALREADY_ASKED_FIELD_NUMBER: _ClassVar[int]
        WAITING_FIELD_NUMBER: _ClassVar[int]
        accepted: SurrenderInfoResponse.SurrenderVoteResponse.SurrenderVoteAccepted
        refused: SurrenderInfoResponse.SurrenderVoteResponse.SurrenderVoteRefused
        before_turn: SurrenderInfoResponse.SurrenderVoteResponse.SurrenderVoteBeforeTurn
        already_asked: SurrenderInfoResponse.SurrenderVoteResponse.SurrenderVoteAlreadyAsked
        waiting: SurrenderInfoResponse.SurrenderVoteResponse.SurrenderVoteWaiting
        def __init__(self, accepted: _Optional[_Union[SurrenderInfoResponse.SurrenderVoteResponse.SurrenderVoteAccepted, _Mapping]] = ..., refused: _Optional[_Union[SurrenderInfoResponse.SurrenderVoteResponse.SurrenderVoteRefused, _Mapping]] = ..., before_turn: _Optional[_Union[SurrenderInfoResponse.SurrenderVoteResponse.SurrenderVoteBeforeTurn, _Mapping]] = ..., already_asked: _Optional[_Union[SurrenderInfoResponse.SurrenderVoteResponse.SurrenderVoteAlreadyAsked, _Mapping]] = ..., waiting: _Optional[_Union[SurrenderInfoResponse.SurrenderVoteResponse.SurrenderVoteWaiting, _Mapping]] = ...) -> None: ...
    SURRENDER_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    SURRENDER_VOTE_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    HAS_SANCTION_FIELD_NUMBER: _ClassVar[int]
    surrender_response: SurrenderInfoResponse.SurrenderResponse
    surrender_vote_response: SurrenderInfoResponse.SurrenderVoteResponse
    has_sanction: bool
    def __init__(self, surrender_response: _Optional[_Union[SurrenderInfoResponse.SurrenderResponse, _Mapping]] = ..., surrender_vote_response: _Optional[_Union[SurrenderInfoResponse.SurrenderVoteResponse, _Mapping]] = ..., has_sanction: bool = ...) -> None: ...

class SurrenderVoteCastRequest(_message.Message):
    __slots__ = ("vote",)
    VOTE_FIELD_NUMBER: _ClassVar[int]
    vote: bool
    def __init__(self, vote: bool = ...) -> None: ...

class SurrenderVoteStartEvent(_message.Message):
    __slots__ = ("already_casted_vote", "participant_number", "casted_vote_number", "vote_duration")
    ALREADY_CASTED_VOTE_FIELD_NUMBER: _ClassVar[int]
    PARTICIPANT_NUMBER_FIELD_NUMBER: _ClassVar[int]
    CASTED_VOTE_NUMBER_FIELD_NUMBER: _ClassVar[int]
    VOTE_DURATION_FIELD_NUMBER: _ClassVar[int]
    already_casted_vote: bool
    participant_number: int
    casted_vote_number: int
    vote_duration: int
    def __init__(self, already_casted_vote: bool = ..., participant_number: _Optional[int] = ..., casted_vote_number: _Optional[int] = ..., vote_duration: _Optional[int] = ...) -> None: ...

class SurrenderVoteUpdateEvent(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SurrenderVoteEndEvent(_message.Message):
    __slots__ = ("voteResult",)
    VOTERESULT_FIELD_NUMBER: _ClassVar[int]
    voteResult: bool
    def __init__(self, voteResult: bool = ...) -> None: ...

class OpponentSurrenderEvent(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
