import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AVAStateUpdateRequest(_message.Message):
    __slots__ = ("enable",)
    ENABLE_FIELD_NUMBER: _ClassVar[int]
    enable: bool
    def __init__(self, enable: bool = ...) -> None: ...

class AllianceFightListenStartRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class AllianceFightListenStopRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class AllianceFightJoinRequest(_message.Message):
    __slots__ = ("fight_information",)
    FIGHT_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    fight_information: _common_pb2.SocialFightInformation
    def __init__(self, fight_information: _Optional[_Union[_common_pb2.SocialFightInformation, _Mapping]] = ...) -> None: ...

class AllianceFightReplaceRequest(_message.Message):
    __slots__ = ("fight_information", "to_replace_fighter_id")
    FIGHT_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    TO_REPLACE_FIGHTER_ID_FIELD_NUMBER: _ClassVar[int]
    fight_information: _common_pb2.SocialFightInformation
    to_replace_fighter_id: int
    def __init__(self, fight_information: _Optional[_Union[_common_pb2.SocialFightInformation, _Mapping]] = ..., to_replace_fighter_id: _Optional[int] = ...) -> None: ...

class AllianceFightLeaveRequest(_message.Message):
    __slots__ = ("fight_information",)
    FIGHT_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    fight_information: _common_pb2.SocialFightInformation
    def __init__(self, fight_information: _Optional[_Union[_common_pb2.SocialFightInformation, _Mapping]] = ...) -> None: ...

class AllianceFightsInformationEvent(_message.Message):
    __slots__ = ("alliance_fights",)
    ALLIANCE_FIGHTS_FIELD_NUMBER: _ClassVar[int]
    alliance_fights: _containers.RepeatedCompositeFieldContainer[_common_pb2.SocialFight]
    def __init__(self, alliance_fights: _Optional[_Iterable[_Union[_common_pb2.SocialFight, _Mapping]]] = ...) -> None: ...

class AllianceFightStartedEvent(_message.Message):
    __slots__ = ("fight_information", "phase")
    FIGHT_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    PHASE_FIELD_NUMBER: _ClassVar[int]
    fight_information: _common_pb2.SocialFightInformation
    phase: _common_pb2.FightPhaseInfo
    def __init__(self, fight_information: _Optional[_Union[_common_pb2.SocialFightInformation, _Mapping]] = ..., phase: _Optional[_Union[_common_pb2.FightPhaseInfo, _Mapping]] = ...) -> None: ...

class AllianceFightFinishedEvent(_message.Message):
    __slots__ = ("fight_information",)
    FIGHT_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    fight_information: _common_pb2.SocialFightInformation
    def __init__(self, fight_information: _Optional[_Union[_common_pb2.SocialFightInformation, _Mapping]] = ...) -> None: ...

class AllianceFightPhaseUpdateEvent(_message.Message):
    __slots__ = ("fight_information", "phase")
    FIGHT_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    PHASE_FIELD_NUMBER: _ClassVar[int]
    fight_information: _common_pb2.SocialFightInformation
    phase: _common_pb2.FightPhaseInfo
    def __init__(self, fight_information: _Optional[_Union[_common_pb2.SocialFightInformation, _Mapping]] = ..., phase: _Optional[_Union[_common_pb2.FightPhaseInfo, _Mapping]] = ...) -> None: ...

class AllianceFightFighterAddedEvent(_message.Message):
    __slots__ = ("fight_information", "fighter", "team")
    FIGHT_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    FIGHTER_FIELD_NUMBER: _ClassVar[int]
    TEAM_FIELD_NUMBER: _ClassVar[int]
    fight_information: _common_pb2.SocialFightInformation
    fighter: _common_pb2.Character
    team: _common_pb2.Team
    def __init__(self, fight_information: _Optional[_Union[_common_pb2.SocialFightInformation, _Mapping]] = ..., fighter: _Optional[_Union[_common_pb2.Character, _Mapping]] = ..., team: _Optional[_Union[_common_pb2.Team, str]] = ...) -> None: ...

class AllianceFightFighterRemovedEvent(_message.Message):
    __slots__ = ("fight_information", "fighter_id")
    FIGHT_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    FIGHTER_ID_FIELD_NUMBER: _ClassVar[int]
    fight_information: _common_pb2.SocialFightInformation
    fighter_id: int
    def __init__(self, fight_information: _Optional[_Union[_common_pb2.SocialFightInformation, _Mapping]] = ..., fighter_id: _Optional[int] = ...) -> None: ...

class KOTHUpdateEvent(_message.Message):
    __slots__ = ("koth_alliance_information", "starting_ava_timestamp", "next_tick_time")
    class KOTHAllianceInformation(_message.Message):
        __slots__ = ("alliance", "member_count", "koth_roles", "scores", "match_domination_scores")
        class KOTHAllianceRoleNumber(_message.Message):
            __slots__ = ("member_count", "koth_role")
            MEMBER_COUNT_FIELD_NUMBER: _ClassVar[int]
            KOTH_ROLE_FIELD_NUMBER: _ClassVar[int]
            member_count: int
            koth_role: int
            def __init__(self, member_count: _Optional[int] = ..., koth_role: _Optional[int] = ...) -> None: ...
        class KOTHScore(_message.Message):
            __slots__ = ("score_type", "round_scores", "cumulated_scores")
            class KOTHScoreType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
                __slots__ = ()
                FIGHT: _ClassVar[KOTHUpdateEvent.KOTHAllianceInformation.KOTHScore.KOTHScoreType]
                DOMINATION: _ClassVar[KOTHUpdateEvent.KOTHAllianceInformation.KOTHScore.KOTHScoreType]
                PRISM: _ClassVar[KOTHUpdateEvent.KOTHAllianceInformation.KOTHScore.KOTHScoreType]
            FIGHT: KOTHUpdateEvent.KOTHAllianceInformation.KOTHScore.KOTHScoreType
            DOMINATION: KOTHUpdateEvent.KOTHAllianceInformation.KOTHScore.KOTHScoreType
            PRISM: KOTHUpdateEvent.KOTHAllianceInformation.KOTHScore.KOTHScoreType
            SCORE_TYPE_FIELD_NUMBER: _ClassVar[int]
            ROUND_SCORES_FIELD_NUMBER: _ClassVar[int]
            CUMULATED_SCORES_FIELD_NUMBER: _ClassVar[int]
            score_type: KOTHUpdateEvent.KOTHAllianceInformation.KOTHScore.KOTHScoreType
            round_scores: int
            cumulated_scores: int
            def __init__(self, score_type: _Optional[_Union[KOTHUpdateEvent.KOTHAllianceInformation.KOTHScore.KOTHScoreType, str]] = ..., round_scores: _Optional[int] = ..., cumulated_scores: _Optional[int] = ...) -> None: ...
        ALLIANCE_FIELD_NUMBER: _ClassVar[int]
        MEMBER_COUNT_FIELD_NUMBER: _ClassVar[int]
        KOTH_ROLES_FIELD_NUMBER: _ClassVar[int]
        SCORES_FIELD_NUMBER: _ClassVar[int]
        MATCH_DOMINATION_SCORES_FIELD_NUMBER: _ClassVar[int]
        alliance: _common_pb2.AllianceInformation
        member_count: int
        koth_roles: _containers.RepeatedCompositeFieldContainer[KOTHUpdateEvent.KOTHAllianceInformation.KOTHAllianceRoleNumber]
        scores: _containers.RepeatedCompositeFieldContainer[KOTHUpdateEvent.KOTHAllianceInformation.KOTHScore]
        match_domination_scores: int
        def __init__(self, alliance: _Optional[_Union[_common_pb2.AllianceInformation, _Mapping]] = ..., member_count: _Optional[int] = ..., koth_roles: _Optional[_Iterable[_Union[KOTHUpdateEvent.KOTHAllianceInformation.KOTHAllianceRoleNumber, _Mapping]]] = ..., scores: _Optional[_Iterable[_Union[KOTHUpdateEvent.KOTHAllianceInformation.KOTHScore, _Mapping]]] = ..., match_domination_scores: _Optional[int] = ...) -> None: ...
    KOTH_ALLIANCE_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    STARTING_AVA_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    NEXT_TICK_TIME_FIELD_NUMBER: _ClassVar[int]
    koth_alliance_information: _containers.RepeatedCompositeFieldContainer[KOTHUpdateEvent.KOTHAllianceInformation]
    starting_ava_timestamp: str
    next_tick_time: int
    def __init__(self, koth_alliance_information: _Optional[_Iterable[_Union[KOTHUpdateEvent.KOTHAllianceInformation, _Mapping]]] = ..., starting_ava_timestamp: _Optional[str] = ..., next_tick_time: _Optional[int] = ...) -> None: ...

class KOTHEndEvent(_message.Message):
    __slots__ = ("winner",)
    WINNER_FIELD_NUMBER: _ClassVar[int]
    winner: _common_pb2.AllianceInformation
    def __init__(self, winner: _Optional[_Union[_common_pb2.AllianceInformation, _Mapping]] = ...) -> None: ...

class NuggetsBeneficiary(_message.Message):
    __slots__ = ("character_id", "nuggets_quantity")
    CHARACTER_ID_FIELD_NUMBER: _ClassVar[int]
    NUGGETS_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    character_id: int
    nuggets_quantity: int
    def __init__(self, character_id: _Optional[int] = ..., nuggets_quantity: _Optional[int] = ...) -> None: ...

class NuggetsDistributionRequest(_message.Message):
    __slots__ = ("beneficiaries",)
    BENEFICIARIES_FIELD_NUMBER: _ClassVar[int]
    beneficiaries: _containers.RepeatedCompositeFieldContainer[NuggetsBeneficiary]
    def __init__(self, beneficiaries: _Optional[_Iterable[_Union[NuggetsBeneficiary, _Mapping]]] = ...) -> None: ...

class NuggetsListenStartRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class NuggetsListenStopRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class NuggetsInformationEvent(_message.Message):
    __slots__ = ("nuggets_quantity",)
    NUGGETS_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    nuggets_quantity: int
    def __init__(self, nuggets_quantity: _Optional[int] = ...) -> None: ...
