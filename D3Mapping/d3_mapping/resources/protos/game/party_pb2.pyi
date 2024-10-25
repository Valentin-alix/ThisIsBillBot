import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PartyMemberInFightCause(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN: _ClassVar[PartyMemberInFightCause]
    MONSTER_ATTACK: _ClassVar[PartyMemberInFightCause]
    PLAYER_ATTACK: _ClassVar[PartyMemberInFightCause]
    MEMBER_ATTACKED_PLAYERS: _ClassVar[PartyMemberInFightCause]
    MEMBER_CHALLENGE: _ClassVar[PartyMemberInFightCause]

class PartyType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNDEFINED: _ClassVar[PartyType]
    CLASSICAL: _ClassVar[PartyType]
    ARENA: _ClassVar[PartyType]
UNKNOWN: PartyMemberInFightCause
MONSTER_ATTACK: PartyMemberInFightCause
PLAYER_ATTACK: PartyMemberInFightCause
MEMBER_ATTACKED_PLAYERS: PartyMemberInFightCause
MEMBER_CHALLENGE: PartyMemberInFightCause
UNDEFINED: PartyType
CLASSICAL: PartyType
ARENA: PartyType

class PartyInvitationRequest(_message.Message):
    __slots__ = ("target", "party_type")
    TARGET_FIELD_NUMBER: _ClassVar[int]
    PARTY_TYPE_FIELD_NUMBER: _ClassVar[int]
    target: _common_pb2.PlayerSearch
    party_type: PartyType
    def __init__(self, target: _Optional[_Union[_common_pb2.PlayerSearch, _Mapping]] = ..., party_type: _Optional[_Union[PartyType, str]] = ...) -> None: ...

class PartyInvitationDetailsRequest(_message.Message):
    __slots__ = ("party_id",)
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    party_id: int
    def __init__(self, party_id: _Optional[int] = ...) -> None: ...

class PartyInvitationAcceptRequest(_message.Message):
    __slots__ = ("party_id",)
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    party_id: int
    def __init__(self, party_id: _Optional[int] = ...) -> None: ...

class PartyInvitationRefuseRequest(_message.Message):
    __slots__ = ("party_id",)
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    party_id: int
    def __init__(self, party_id: _Optional[int] = ...) -> None: ...

class PartyInvitationCancelRequest(_message.Message):
    __slots__ = ("party_id", "guest_id")
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    GUEST_ID_FIELD_NUMBER: _ClassVar[int]
    party_id: int
    guest_id: int
    def __init__(self, party_id: _Optional[int] = ..., guest_id: _Optional[int] = ...) -> None: ...

class PartyAbdicateThroneRequest(_message.Message):
    __slots__ = ("party_id", "player_id")
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
    party_id: int
    player_id: int
    def __init__(self, party_id: _Optional[int] = ..., player_id: _Optional[int] = ...) -> None: ...

class PartyFollowMemberRequest(_message.Message):
    __slots__ = ("party_id", "player_id", "enabled")
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
    ENABLED_FIELD_NUMBER: _ClassVar[int]
    party_id: int
    player_id: int
    enabled: bool
    def __init__(self, party_id: _Optional[int] = ..., player_id: _Optional[int] = ..., enabled: bool = ...) -> None: ...

class PartyStopFollowMemberRequest(_message.Message):
    __slots__ = ("party_id", "player_id")
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
    party_id: int
    player_id: int
    def __init__(self, party_id: _Optional[int] = ..., player_id: _Optional[int] = ...) -> None: ...

class PartyLocateMembersRequest(_message.Message):
    __slots__ = ("party_id",)
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    party_id: int
    def __init__(self, party_id: _Optional[int] = ...) -> None: ...

class PartyLeaveRequest(_message.Message):
    __slots__ = ("party_id",)
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    party_id: int
    def __init__(self, party_id: _Optional[int] = ...) -> None: ...

class PartyKickRequest(_message.Message):
    __slots__ = ("party_id", "player_id")
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
    party_id: int
    player_id: int
    def __init__(self, party_id: _Optional[int] = ..., player_id: _Optional[int] = ...) -> None: ...

class PartyPledgeLoyaltyRequest(_message.Message):
    __slots__ = ("party_id", "loyal")
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    LOYAL_FIELD_NUMBER: _ClassVar[int]
    party_id: int
    loyal: bool
    def __init__(self, party_id: _Optional[int] = ..., loyal: bool = ...) -> None: ...

class PartyNameSetRequest(_message.Message):
    __slots__ = ("party_id", "name")
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    party_id: int
    name: str
    def __init__(self, party_id: _Optional[int] = ..., name: _Optional[str] = ...) -> None: ...

class PartyInvitationEvent(_message.Message):
    __slots__ = ("party_id", "party_type", "party_name", "max_participants", "from_player_id", "from_player_name", "to_player_id")
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    PARTY_TYPE_FIELD_NUMBER: _ClassVar[int]
    PARTY_NAME_FIELD_NUMBER: _ClassVar[int]
    MAX_PARTICIPANTS_FIELD_NUMBER: _ClassVar[int]
    FROM_PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
    FROM_PLAYER_NAME_FIELD_NUMBER: _ClassVar[int]
    TO_PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
    party_id: int
    party_type: PartyType
    party_name: str
    max_participants: int
    from_player_id: int
    from_player_name: str
    to_player_id: int
    def __init__(self, party_id: _Optional[int] = ..., party_type: _Optional[_Union[PartyType, str]] = ..., party_name: _Optional[str] = ..., max_participants: _Optional[int] = ..., from_player_id: _Optional[int] = ..., from_player_name: _Optional[str] = ..., to_player_id: _Optional[int] = ...) -> None: ...

class PartyInvitationDetailsEvent(_message.Message):
    __slots__ = ("party_id", "party_type", "party_name", "from_player_id", "from_player_name", "leader_id", "members", "guests")
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    PARTY_TYPE_FIELD_NUMBER: _ClassVar[int]
    PARTY_NAME_FIELD_NUMBER: _ClassVar[int]
    FROM_PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
    FROM_PLAYER_NAME_FIELD_NUMBER: _ClassVar[int]
    LEADER_ID_FIELD_NUMBER: _ClassVar[int]
    MEMBERS_FIELD_NUMBER: _ClassVar[int]
    GUESTS_FIELD_NUMBER: _ClassVar[int]
    party_id: int
    party_type: PartyType
    party_name: str
    from_player_id: int
    from_player_name: str
    leader_id: int
    members: _containers.RepeatedCompositeFieldContainer[_common_pb2.Character]
    guests: _containers.RepeatedCompositeFieldContainer[PartyGuest]
    def __init__(self, party_id: _Optional[int] = ..., party_type: _Optional[_Union[PartyType, str]] = ..., party_name: _Optional[str] = ..., from_player_id: _Optional[int] = ..., from_player_name: _Optional[str] = ..., leader_id: _Optional[int] = ..., members: _Optional[_Iterable[_Union[_common_pb2.Character, _Mapping]]] = ..., guests: _Optional[_Iterable[_Union[PartyGuest, _Mapping]]] = ...) -> None: ...

class PartyInvitationCancelledForGuestEvent(_message.Message):
    __slots__ = ("party_id", "canceller_id")
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    CANCELLER_ID_FIELD_NUMBER: _ClassVar[int]
    party_id: int
    canceller_id: int
    def __init__(self, party_id: _Optional[int] = ..., canceller_id: _Optional[int] = ...) -> None: ...

class PartyInvitationCancelledEvent(_message.Message):
    __slots__ = ("party_id", "canceller_id", "guest_id")
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    CANCELLER_ID_FIELD_NUMBER: _ClassVar[int]
    GUEST_ID_FIELD_NUMBER: _ClassVar[int]
    party_id: int
    canceller_id: int
    guest_id: int
    def __init__(self, party_id: _Optional[int] = ..., canceller_id: _Optional[int] = ..., guest_id: _Optional[int] = ...) -> None: ...

class PartyInvitationRefusedEvent(_message.Message):
    __slots__ = ("party_id", "guest_id")
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    GUEST_ID_FIELD_NUMBER: _ClassVar[int]
    party_id: int
    guest_id: int
    def __init__(self, party_id: _Optional[int] = ..., guest_id: _Optional[int] = ...) -> None: ...

class PartyJoinErrorEvent(_message.Message):
    __slots__ = ("party_id", "reason")
    class PartyJoinError(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN: _ClassVar[PartyJoinErrorEvent.PartyJoinError]
        PLAYER_NOT_FOUND: _ClassVar[PartyJoinErrorEvent.PartyJoinError]
        PARTY_NOT_FOUND: _ClassVar[PartyJoinErrorEvent.PartyJoinError]
        PARTY_FULL: _ClassVar[PartyJoinErrorEvent.PartyJoinError]
        PLAYER_BUSY: _ClassVar[PartyJoinErrorEvent.PartyJoinError]
        PLAYER_ALREADY_INVITED: _ClassVar[PartyJoinErrorEvent.PartyJoinError]
        PLAYER_TOO_SOLICITED: _ClassVar[PartyJoinErrorEvent.PartyJoinError]
        PLAYER_LOYAL: _ClassVar[PartyJoinErrorEvent.PartyJoinError]
        UNMODIFIABLE: _ClassVar[PartyJoinErrorEvent.PartyJoinError]
        UNMET_CRITERION: _ClassVar[PartyJoinErrorEvent.PartyJoinError]
        NOT_ENOUGH_ROOM: _ClassVar[PartyJoinErrorEvent.PartyJoinError]
        COMPOSITION_CHANGED: _ClassVar[PartyJoinErrorEvent.PartyJoinError]
        PLAYER_IN_TUTORIAL: _ClassVar[PartyJoinErrorEvent.PartyJoinError]
    UNKNOWN: PartyJoinErrorEvent.PartyJoinError
    PLAYER_NOT_FOUND: PartyJoinErrorEvent.PartyJoinError
    PARTY_NOT_FOUND: PartyJoinErrorEvent.PartyJoinError
    PARTY_FULL: PartyJoinErrorEvent.PartyJoinError
    PLAYER_BUSY: PartyJoinErrorEvent.PartyJoinError
    PLAYER_ALREADY_INVITED: PartyJoinErrorEvent.PartyJoinError
    PLAYER_TOO_SOLICITED: PartyJoinErrorEvent.PartyJoinError
    PLAYER_LOYAL: PartyJoinErrorEvent.PartyJoinError
    UNMODIFIABLE: PartyJoinErrorEvent.PartyJoinError
    UNMET_CRITERION: PartyJoinErrorEvent.PartyJoinError
    NOT_ENOUGH_ROOM: PartyJoinErrorEvent.PartyJoinError
    COMPOSITION_CHANGED: PartyJoinErrorEvent.PartyJoinError
    PLAYER_IN_TUTORIAL: PartyJoinErrorEvent.PartyJoinError
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    party_id: int
    reason: PartyJoinErrorEvent.PartyJoinError
    def __init__(self, party_id: _Optional[int] = ..., reason: _Optional[_Union[PartyJoinErrorEvent.PartyJoinError, str]] = ...) -> None: ...

class PartyJoinEvent(_message.Message):
    __slots__ = ("party_id", "party_type", "leader_id", "max_participants", "members", "guests", "restricted", "party_name")
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    PARTY_TYPE_FIELD_NUMBER: _ClassVar[int]
    LEADER_ID_FIELD_NUMBER: _ClassVar[int]
    MAX_PARTICIPANTS_FIELD_NUMBER: _ClassVar[int]
    MEMBERS_FIELD_NUMBER: _ClassVar[int]
    GUESTS_FIELD_NUMBER: _ClassVar[int]
    RESTRICTED_FIELD_NUMBER: _ClassVar[int]
    PARTY_NAME_FIELD_NUMBER: _ClassVar[int]
    party_id: int
    party_type: PartyType
    leader_id: int
    max_participants: int
    members: _containers.RepeatedCompositeFieldContainer[_common_pb2.Character]
    guests: _containers.RepeatedCompositeFieldContainer[PartyGuest]
    restricted: bool
    party_name: str
    def __init__(self, party_id: _Optional[int] = ..., party_type: _Optional[_Union[PartyType, str]] = ..., leader_id: _Optional[int] = ..., max_participants: _Optional[int] = ..., members: _Optional[_Iterable[_Union[_common_pb2.Character, _Mapping]]] = ..., guests: _Optional[_Iterable[_Union[PartyGuest, _Mapping]]] = ..., restricted: bool = ..., party_name: _Optional[str] = ...) -> None: ...

class PartyNewGuestEvent(_message.Message):
    __slots__ = ("party_id", "guest")
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    GUEST_FIELD_NUMBER: _ClassVar[int]
    party_id: int
    guest: PartyGuest
    def __init__(self, party_id: _Optional[int] = ..., guest: _Optional[_Union[PartyGuest, _Mapping]] = ...) -> None: ...

class PartyMemberUpdateEvent(_message.Message):
    __slots__ = ("party_id", "member")
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    MEMBER_FIELD_NUMBER: _ClassVar[int]
    party_id: int
    member: _common_pb2.Character
    def __init__(self, party_id: _Optional[int] = ..., member: _Optional[_Union[_common_pb2.Character, _Mapping]] = ...) -> None: ...

class PartyNewMemberEvent(_message.Message):
    __slots__ = ("party_id", "member")
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    MEMBER_FIELD_NUMBER: _ClassVar[int]
    party_id: int
    member: _common_pb2.Character
    def __init__(self, party_id: _Optional[int] = ..., member: _Optional[_Union[_common_pb2.Character, _Mapping]] = ...) -> None: ...

class PartyMemberUpdateLightEvent(_message.Message):
    __slots__ = ("party_id", "player_id", "commons_information", "index")
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
    COMMONS_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    party_id: int
    player_id: int
    commons_information: _common_pb2.PartyUpdateCommonsInformation
    index: int
    def __init__(self, party_id: _Optional[int] = ..., player_id: _Optional[int] = ..., commons_information: _Optional[_Union[_common_pb2.PartyUpdateCommonsInformation, _Mapping]] = ..., index: _Optional[int] = ...) -> None: ...

class PartyMemberRemoveEvent(_message.Message):
    __slots__ = ("party_id", "leaving_player_id", "kicker_id")
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    LEAVING_PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
    KICKER_ID_FIELD_NUMBER: _ClassVar[int]
    party_id: int
    leaving_player_id: int
    kicker_id: int
    def __init__(self, party_id: _Optional[int] = ..., leaving_player_id: _Optional[int] = ..., kicker_id: _Optional[int] = ...) -> None: ...

class PartyLeaderUpdateEvent(_message.Message):
    __slots__ = ("party_id", "party_leader_id")
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    PARTY_LEADER_ID_FIELD_NUMBER: _ClassVar[int]
    party_id: int
    party_leader_id: int
    def __init__(self, party_id: _Optional[int] = ..., party_leader_id: _Optional[int] = ...) -> None: ...

class PartyFollowStatusUpdateEvent(_message.Message):
    __slots__ = ("party_id", "success", "is_followed", "followed_id")
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    IS_FOLLOWED_FIELD_NUMBER: _ClassVar[int]
    FOLLOWED_ID_FIELD_NUMBER: _ClassVar[int]
    party_id: int
    success: bool
    is_followed: bool
    followed_id: int
    def __init__(self, party_id: _Optional[int] = ..., success: bool = ..., is_followed: bool = ..., followed_id: _Optional[int] = ...) -> None: ...

class PartyLeaveEvent(_message.Message):
    __slots__ = ("party_id",)
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    party_id: int
    def __init__(self, party_id: _Optional[int] = ...) -> None: ...

class PartyKickedByEvent(_message.Message):
    __slots__ = ("party_id", "kicker_id")
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    KICKER_ID_FIELD_NUMBER: _ClassVar[int]
    party_id: int
    kicker_id: int
    def __init__(self, party_id: _Optional[int] = ..., kicker_id: _Optional[int] = ...) -> None: ...

class PartyRestrictedEvent(_message.Message):
    __slots__ = ("party_id", "restricted")
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    RESTRICTED_FIELD_NUMBER: _ClassVar[int]
    party_id: int
    restricted: bool
    def __init__(self, party_id: _Optional[int] = ..., restricted: bool = ...) -> None: ...

class PartyDeletedEvent(_message.Message):
    __slots__ = ("party_id",)
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    party_id: int
    def __init__(self, party_id: _Optional[int] = ...) -> None: ...

class PartyLoyaltyStatusEvent(_message.Message):
    __slots__ = ("party_id", "loyal")
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    LOYAL_FIELD_NUMBER: _ClassVar[int]
    party_id: int
    loyal: bool
    def __init__(self, party_id: _Optional[int] = ..., loyal: bool = ...) -> None: ...

class PartyMemberInFightEvent(_message.Message):
    __slots__ = ("party_id", "reason", "member_id", "member_account_id", "member_name", "fight_id", "time_before_fight_start", "standard_fight_map")
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    MEMBER_ID_FIELD_NUMBER: _ClassVar[int]
    MEMBER_ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    MEMBER_NAME_FIELD_NUMBER: _ClassVar[int]
    FIGHT_ID_FIELD_NUMBER: _ClassVar[int]
    TIME_BEFORE_FIGHT_START_FIELD_NUMBER: _ClassVar[int]
    STANDARD_FIGHT_MAP_FIELD_NUMBER: _ClassVar[int]
    party_id: int
    reason: PartyMemberInFightCause
    member_id: int
    member_account_id: int
    member_name: str
    fight_id: int
    time_before_fight_start: int
    standard_fight_map: _common_pb2.MapExtendedCoordinates
    def __init__(self, party_id: _Optional[int] = ..., reason: _Optional[_Union[PartyMemberInFightCause, str]] = ..., member_id: _Optional[int] = ..., member_account_id: _Optional[int] = ..., member_name: _Optional[str] = ..., fight_id: _Optional[int] = ..., time_before_fight_start: _Optional[int] = ..., standard_fight_map: _Optional[_Union[_common_pb2.MapExtendedCoordinates, _Mapping]] = ...) -> None: ...

class PartyMemberInBreachFightEvent(_message.Message):
    __slots__ = ("party_id", "reason", "member_id", "member_account_id", "member_name", "fight_id", "time_before_fight_start", "floor", "room")
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    MEMBER_ID_FIELD_NUMBER: _ClassVar[int]
    MEMBER_ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    MEMBER_NAME_FIELD_NUMBER: _ClassVar[int]
    FIGHT_ID_FIELD_NUMBER: _ClassVar[int]
    TIME_BEFORE_FIGHT_START_FIELD_NUMBER: _ClassVar[int]
    FLOOR_FIELD_NUMBER: _ClassVar[int]
    ROOM_FIELD_NUMBER: _ClassVar[int]
    party_id: int
    reason: PartyMemberInFightCause
    member_id: int
    member_account_id: int
    member_name: str
    fight_id: int
    time_before_fight_start: int
    floor: int
    room: int
    def __init__(self, party_id: _Optional[int] = ..., reason: _Optional[_Union[PartyMemberInFightCause, str]] = ..., member_id: _Optional[int] = ..., member_account_id: _Optional[int] = ..., member_name: _Optional[str] = ..., fight_id: _Optional[int] = ..., time_before_fight_start: _Optional[int] = ..., floor: _Optional[int] = ..., room: _Optional[int] = ...) -> None: ...

class PartyNameUpdateEvent(_message.Message):
    __slots__ = ("party_id", "name")
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    party_id: int
    name: str
    def __init__(self, party_id: _Optional[int] = ..., name: _Optional[str] = ...) -> None: ...

class PartyNameSetErrorEvent(_message.Message):
    __slots__ = ("party_id", "result")
    class PartyNameError(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNDEFINED_ERROR: _ClassVar[PartyNameSetErrorEvent.PartyNameError]
        INVALID: _ClassVar[PartyNameSetErrorEvent.PartyNameError]
        ALREADY_USED: _ClassVar[PartyNameSetErrorEvent.PartyNameError]
        UNALLOWED_RIGHTS: _ClassVar[PartyNameSetErrorEvent.PartyNameError]
        UNALLOWED_NOW: _ClassVar[PartyNameSetErrorEvent.PartyNameError]
    UNDEFINED_ERROR: PartyNameSetErrorEvent.PartyNameError
    INVALID: PartyNameSetErrorEvent.PartyNameError
    ALREADY_USED: PartyNameSetErrorEvent.PartyNameError
    UNALLOWED_RIGHTS: PartyNameSetErrorEvent.PartyNameError
    UNALLOWED_NOW: PartyNameSetErrorEvent.PartyNameError
    PARTY_ID_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    party_id: int
    result: PartyNameSetErrorEvent.PartyNameError
    def __init__(self, party_id: _Optional[int] = ..., result: _Optional[_Union[PartyNameSetErrorEvent.PartyNameError, str]] = ...) -> None: ...

class PartyGuest(_message.Message):
    __slots__ = ("player_id", "host_id", "name", "look", "breed", "gender", "status", "entities")
    PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
    HOST_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    LOOK_FIELD_NUMBER: _ClassVar[int]
    BREED_FIELD_NUMBER: _ClassVar[int]
    GENDER_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ENTITIES_FIELD_NUMBER: _ClassVar[int]
    player_id: int
    host_id: int
    name: str
    look: _common_pb2.EntityLook
    breed: int
    gender: _common_pb2.Gender
    status: _common_pb2.CharacterStatus
    entities: _containers.RepeatedCompositeFieldContainer[_common_pb2.PartyEntity]
    def __init__(self, player_id: _Optional[int] = ..., host_id: _Optional[int] = ..., name: _Optional[str] = ..., look: _Optional[_Union[_common_pb2.EntityLook, _Mapping]] = ..., breed: _Optional[int] = ..., gender: _Optional[_Union[_common_pb2.Gender, str]] = ..., status: _Optional[_Union[_common_pb2.CharacterStatus, _Mapping]] = ..., entities: _Optional[_Iterable[_Union[_common_pb2.PartyEntity, _Mapping]]] = ...) -> None: ...
