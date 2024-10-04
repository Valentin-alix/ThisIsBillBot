from com.ankama.dofus.server.game.protocol import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AddFailureReason(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN: _ClassVar[AddFailureReason]
    OVER_QUOTA: _ClassVar[AddFailureReason]
    NOT_FOUND: _ClassVar[AddFailureReason]
    EGOCENTRIC: _ClassVar[AddFailureReason]
    IS_DOUBLE: _ClassVar[AddFailureReason]
    IS_CONFLICTING_DOUBLE: _ClassVar[AddFailureReason]
UNKNOWN: AddFailureReason
OVER_QUOTA: AddFailureReason
NOT_FOUND: AddFailureReason
EGOCENTRIC: AddFailureReason
IS_DOUBLE: AddFailureReason
IS_CONFLICTING_DOUBLE: AddFailureReason

class ContactWarnOnAchievementCompleteSetRequest(_message.Message):
    __slots__ = ("enable",)
    ENABLE_FIELD_NUMBER: _ClassVar[int]
    enable: bool
    def __init__(self, enable: bool = ...) -> None: ...

class ContactLookRequest(_message.Message):
    __slots__ = ("request_id", "contact_type", "name", "id")
    class SocialContactCategory(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        FRIEND: _ClassVar[ContactLookRequest.SocialContactCategory]
        SPOUSE: _ClassVar[ContactLookRequest.SocialContactCategory]
        PARTY: _ClassVar[ContactLookRequest.SocialContactCategory]
        GUILD: _ClassVar[ContactLookRequest.SocialContactCategory]
        ALLIANCE: _ClassVar[ContactLookRequest.SocialContactCategory]
        CRAFTER: _ClassVar[ContactLookRequest.SocialContactCategory]
        INTERLOCUTOR: _ClassVar[ContactLookRequest.SocialContactCategory]
        FIGHT: _ClassVar[ContactLookRequest.SocialContactCategory]
    FRIEND: ContactLookRequest.SocialContactCategory
    SPOUSE: ContactLookRequest.SocialContactCategory
    PARTY: ContactLookRequest.SocialContactCategory
    GUILD: ContactLookRequest.SocialContactCategory
    ALLIANCE: ContactLookRequest.SocialContactCategory
    CRAFTER: ContactLookRequest.SocialContactCategory
    INTERLOCUTOR: ContactLookRequest.SocialContactCategory
    FIGHT: ContactLookRequest.SocialContactCategory
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    CONTACT_TYPE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    request_id: int
    contact_type: ContactLookRequest.SocialContactCategory
    name: str
    id: int
    def __init__(self, request_id: _Optional[int] = ..., contact_type: _Optional[_Union[ContactLookRequest.SocialContactCategory, str]] = ..., name: _Optional[str] = ..., id: _Optional[int] = ...) -> None: ...

class FriendAddRequest(_message.Message):
    __slots__ = ("target",)
    TARGET_FIELD_NUMBER: _ClassVar[int]
    target: _common_pb2.PlayerSearch
    def __init__(self, target: _Optional[_Union[_common_pb2.PlayerSearch, _Mapping]] = ...) -> None: ...

class FriendDeleteRequest(_message.Message):
    __slots__ = ("account_id",)
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    account_id: int
    def __init__(self, account_id: _Optional[int] = ...) -> None: ...

class FriendSetWarnOnConnectionRequest(_message.Message):
    __slots__ = ("enable",)
    ENABLE_FIELD_NUMBER: _ClassVar[int]
    enable: bool
    def __init__(self, enable: bool = ...) -> None: ...

class FriendSetWarnOnLevelGainRequest(_message.Message):
    __slots__ = ("enable",)
    ENABLE_FIELD_NUMBER: _ClassVar[int]
    enable: bool
    def __init__(self, enable: bool = ...) -> None: ...

class FriendSetStatusShareRequest(_message.Message):
    __slots__ = ("share",)
    SHARE_FIELD_NUMBER: _ClassVar[int]
    share: bool
    def __init__(self, share: bool = ...) -> None: ...

class IgnoreRequest(_message.Message):
    __slots__ = ("player_search",)
    PLAYER_SEARCH_FIELD_NUMBER: _ClassVar[int]
    player_search: _common_pb2.PlayerSearch
    def __init__(self, player_search: _Optional[_Union[_common_pb2.PlayerSearch, _Mapping]] = ...) -> None: ...

class UnIgnoreRequest(_message.Message):
    __slots__ = ("account_id",)
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    account_id: int
    def __init__(self, account_id: _Optional[int] = ...) -> None: ...

class BlockListRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class BlockRequest(_message.Message):
    __slots__ = ("player_search",)
    PLAYER_SEARCH_FIELD_NUMBER: _ClassVar[int]
    player_search: _common_pb2.PlayerSearch
    def __init__(self, player_search: _Optional[_Union[_common_pb2.PlayerSearch, _Mapping]] = ...) -> None: ...

class UnBlockRequest(_message.Message):
    __slots__ = ("account_id",)
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    account_id: int
    def __init__(self, account_id: _Optional[int] = ...) -> None: ...

class FriendListRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class AcquaintanceListRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ContactWarnOnPermanentDeathSetRequest(_message.Message):
    __slots__ = ("enable",)
    ENABLE_FIELD_NUMBER: _ClassVar[int]
    enable: bool
    def __init__(self, enable: bool = ...) -> None: ...

class ContactWarnOnAchievementCompleteStateEvent(_message.Message):
    __slots__ = ("enable",)
    ENABLE_FIELD_NUMBER: _ClassVar[int]
    enable: bool
    def __init__(self, enable: bool = ...) -> None: ...

class ContactLookEvent(_message.Message):
    __slots__ = ("request_id", "player_name", "player_id", "look")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    PLAYER_NAME_FIELD_NUMBER: _ClassVar[int]
    PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
    LOOK_FIELD_NUMBER: _ClassVar[int]
    request_id: int
    player_name: str
    player_id: int
    look: _common_pb2.EntityLook
    def __init__(self, request_id: _Optional[int] = ..., player_name: _Optional[str] = ..., player_id: _Optional[int] = ..., look: _Optional[_Union[_common_pb2.EntityLook, _Mapping]] = ...) -> None: ...

class ContactLookErrorEvent(_message.Message):
    __slots__ = ("request_id",)
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    request_id: int
    def __init__(self, request_id: _Optional[int] = ...) -> None: ...

class FriendAddFailureEvent(_message.Message):
    __slots__ = ("reason",)
    REASON_FIELD_NUMBER: _ClassVar[int]
    reason: AddFailureReason
    def __init__(self, reason: _Optional[_Union[AddFailureReason, str]] = ...) -> None: ...

class AcquaintanceAddedEvent(_message.Message):
    __slots__ = ("acquaintance",)
    ACQUAINTANCE_FIELD_NUMBER: _ClassVar[int]
    acquaintance: AcquaintanceInformation
    def __init__(self, acquaintance: _Optional[_Union[AcquaintanceInformation, _Mapping]] = ...) -> None: ...

class FriendAddedEvent(_message.Message):
    __slots__ = ("friend",)
    FRIEND_FIELD_NUMBER: _ClassVar[int]
    friend: FriendInformation
    def __init__(self, friend: _Optional[_Union[FriendInformation, _Mapping]] = ...) -> None: ...

class FriendDeletionResultEvent(_message.Message):
    __slots__ = ("success", "account_tag")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_TAG_FIELD_NUMBER: _ClassVar[int]
    success: bool
    account_tag: _common_pb2.AccountTag
    def __init__(self, success: bool = ..., account_tag: _Optional[_Union[_common_pb2.AccountTag, _Mapping]] = ...) -> None: ...

class FriendWarnOnConnectionStateEvent(_message.Message):
    __slots__ = ("enable",)
    ENABLE_FIELD_NUMBER: _ClassVar[int]
    enable: bool
    def __init__(self, enable: bool = ...) -> None: ...

class WarnOnPermanentDeathStateEvent(_message.Message):
    __slots__ = ("enable",)
    ENABLE_FIELD_NUMBER: _ClassVar[int]
    enable: bool
    def __init__(self, enable: bool = ...) -> None: ...

class FriendWarnOnLevelGainStateEvent(_message.Message):
    __slots__ = ("enable",)
    ENABLE_FIELD_NUMBER: _ClassVar[int]
    enable: bool
    def __init__(self, enable: bool = ...) -> None: ...

class FriendStatusShareStateEvent(_message.Message):
    __slots__ = ("share",)
    SHARE_FIELD_NUMBER: _ClassVar[int]
    share: bool
    def __init__(self, share: bool = ...) -> None: ...

class IgnoreEvent(_message.Message):
    __slots__ = ("error", "success")
    class Error(_message.Message):
        __slots__ = ("reason",)
        REASON_FIELD_NUMBER: _ClassVar[int]
        reason: AddFailureReason
        def __init__(self, reason: _Optional[_Union[AddFailureReason, str]] = ...) -> None: ...
    class Success(_message.Message):
        __slots__ = ("ignored",)
        IGNORED_FIELD_NUMBER: _ClassVar[int]
        ignored: ContactInformation
        def __init__(self, ignored: _Optional[_Union[ContactInformation, _Mapping]] = ...) -> None: ...
    ERROR_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    error: IgnoreEvent.Error
    success: IgnoreEvent.Success
    def __init__(self, error: _Optional[_Union[IgnoreEvent.Error, _Mapping]] = ..., success: _Optional[_Union[IgnoreEvent.Success, _Mapping]] = ...) -> None: ...

class UnIgnoreEvent(_message.Message):
    __slots__ = ("error", "success")
    class Error(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class Success(_message.Message):
        __slots__ = ("ignored_tag",)
        IGNORED_TAG_FIELD_NUMBER: _ClassVar[int]
        ignored_tag: _common_pb2.AccountTag
        def __init__(self, ignored_tag: _Optional[_Union[_common_pb2.AccountTag, _Mapping]] = ...) -> None: ...
    ERROR_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    error: UnIgnoreEvent.Error
    success: UnIgnoreEvent.Success
    def __init__(self, error: _Optional[_Union[UnIgnoreEvent.Error, _Mapping]] = ..., success: _Optional[_Union[UnIgnoreEvent.Success, _Mapping]] = ...) -> None: ...

class BlockListEvent(_message.Message):
    __slots__ = ("blocked",)
    BLOCKED_FIELD_NUMBER: _ClassVar[int]
    blocked: _containers.RepeatedCompositeFieldContainer[ContactInformation]
    def __init__(self, blocked: _Optional[_Iterable[_Union[ContactInformation, _Mapping]]] = ...) -> None: ...

class BlockEvent(_message.Message):
    __slots__ = ("error", "success")
    class Error(_message.Message):
        __slots__ = ("reason",)
        REASON_FIELD_NUMBER: _ClassVar[int]
        reason: AddFailureReason
        def __init__(self, reason: _Optional[_Union[AddFailureReason, str]] = ...) -> None: ...
    class Success(_message.Message):
        __slots__ = ("blocked",)
        BLOCKED_FIELD_NUMBER: _ClassVar[int]
        blocked: ContactInformation
        def __init__(self, blocked: _Optional[_Union[ContactInformation, _Mapping]] = ...) -> None: ...
    ERROR_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    error: BlockEvent.Error
    success: BlockEvent.Success
    def __init__(self, error: _Optional[_Union[BlockEvent.Error, _Mapping]] = ..., success: _Optional[_Union[BlockEvent.Success, _Mapping]] = ...) -> None: ...

class UnBlockEvent(_message.Message):
    __slots__ = ("error", "success")
    class Error(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class Success(_message.Message):
        __slots__ = ("tag",)
        TAG_FIELD_NUMBER: _ClassVar[int]
        tag: _common_pb2.AccountTag
        def __init__(self, tag: _Optional[_Union[_common_pb2.AccountTag, _Mapping]] = ...) -> None: ...
    ERROR_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    error: UnBlockEvent.Error
    success: UnBlockEvent.Success
    def __init__(self, error: _Optional[_Union[UnBlockEvent.Error, _Mapping]] = ..., success: _Optional[_Union[UnBlockEvent.Success, _Mapping]] = ...) -> None: ...

class AddContactFailureEvent(_message.Message):
    __slots__ = ("reason",)
    REASON_FIELD_NUMBER: _ClassVar[int]
    reason: AddFailureReason
    def __init__(self, reason: _Optional[_Union[AddFailureReason, str]] = ...) -> None: ...

class FriendListEvent(_message.Message):
    __slots__ = ("friend",)
    FRIEND_FIELD_NUMBER: _ClassVar[int]
    friend: _containers.RepeatedCompositeFieldContainer[FriendInformation]
    def __init__(self, friend: _Optional[_Iterable[_Union[FriendInformation, _Mapping]]] = ...) -> None: ...

class AcquaintanceListEvent(_message.Message):
    __slots__ = ("acquaintance",)
    ACQUAINTANCE_FIELD_NUMBER: _ClassVar[int]
    acquaintance: _containers.RepeatedCompositeFieldContainer[AcquaintanceInformation]
    def __init__(self, acquaintance: _Optional[_Iterable[_Union[AcquaintanceInformation, _Mapping]]] = ...) -> None: ...

class ContactLevelUpEvent(_message.Message):
    __slots__ = ("name", "character_id", "level")
    NAME_FIELD_NUMBER: _ClassVar[int]
    CHARACTER_ID_FIELD_NUMBER: _ClassVar[int]
    LEVEL_FIELD_NUMBER: _ClassVar[int]
    name: str
    character_id: int
    level: int
    def __init__(self, name: _Optional[str] = ..., character_id: _Optional[int] = ..., level: _Optional[int] = ...) -> None: ...

class FriendInformation(_message.Message):
    __slots__ = ("account_id", "account_tag", "state", "duration_since_last_connection_hours", "league_id", "online_information")
    class FriendOnlineInformation(_message.Message):
        __slots__ = ("character_id", "character_name", "character_level", "alignment", "breed_id", "gender", "mood_smiley_id", "haven_bag_shared", "status", "guild", "alliance", "achievement_points", "ladder_position")
        CHARACTER_ID_FIELD_NUMBER: _ClassVar[int]
        CHARACTER_NAME_FIELD_NUMBER: _ClassVar[int]
        CHARACTER_LEVEL_FIELD_NUMBER: _ClassVar[int]
        ALIGNMENT_FIELD_NUMBER: _ClassVar[int]
        BREED_ID_FIELD_NUMBER: _ClassVar[int]
        GENDER_FIELD_NUMBER: _ClassVar[int]
        MOOD_SMILEY_ID_FIELD_NUMBER: _ClassVar[int]
        HAVEN_BAG_SHARED_FIELD_NUMBER: _ClassVar[int]
        STATUS_FIELD_NUMBER: _ClassVar[int]
        GUILD_FIELD_NUMBER: _ClassVar[int]
        ALLIANCE_FIELD_NUMBER: _ClassVar[int]
        ACHIEVEMENT_POINTS_FIELD_NUMBER: _ClassVar[int]
        LADDER_POSITION_FIELD_NUMBER: _ClassVar[int]
        character_id: int
        character_name: str
        character_level: int
        alignment: _common_pb2.Alignment
        breed_id: int
        gender: _common_pb2.Gender
        mood_smiley_id: int
        haven_bag_shared: bool
        status: _common_pb2.CharacterStatus
        guild: _common_pb2.GuildInformation
        alliance: _common_pb2.AllianceInformation
        achievement_points: int
        ladder_position: int
        def __init__(self, character_id: _Optional[int] = ..., character_name: _Optional[str] = ..., character_level: _Optional[int] = ..., alignment: _Optional[_Union[_common_pb2.Alignment, str]] = ..., breed_id: _Optional[int] = ..., gender: _Optional[_Union[_common_pb2.Gender, str]] = ..., mood_smiley_id: _Optional[int] = ..., haven_bag_shared: bool = ..., status: _Optional[_Union[_common_pb2.CharacterStatus, _Mapping]] = ..., guild: _Optional[_Union[_common_pb2.GuildInformation, _Mapping]] = ..., alliance: _Optional[_Union[_common_pb2.AllianceInformation, _Mapping]] = ..., achievement_points: _Optional[int] = ..., ladder_position: _Optional[int] = ...) -> None: ...
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_TAG_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    DURATION_SINCE_LAST_CONNECTION_HOURS_FIELD_NUMBER: _ClassVar[int]
    LEAGUE_ID_FIELD_NUMBER: _ClassVar[int]
    ONLINE_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    account_id: int
    account_tag: _common_pb2.AccountTag
    state: _common_pb2.CharacterState
    duration_since_last_connection_hours: int
    league_id: int
    online_information: FriendInformation.FriendOnlineInformation
    def __init__(self, account_id: _Optional[int] = ..., account_tag: _Optional[_Union[_common_pb2.AccountTag, _Mapping]] = ..., state: _Optional[_Union[_common_pb2.CharacterState, str]] = ..., duration_since_last_connection_hours: _Optional[int] = ..., league_id: _Optional[int] = ..., online_information: _Optional[_Union[FriendInformation.FriendOnlineInformation, _Mapping]] = ...) -> None: ...

class AcquaintanceInformation(_message.Message):
    __slots__ = ("account_id", "account_tag", "state", "online")
    class OnlineInformation(_message.Message):
        __slots__ = ("character_id", "character_name", "mood_smiley_id", "status")
        CHARACTER_ID_FIELD_NUMBER: _ClassVar[int]
        CHARACTER_NAME_FIELD_NUMBER: _ClassVar[int]
        MOOD_SMILEY_ID_FIELD_NUMBER: _ClassVar[int]
        STATUS_FIELD_NUMBER: _ClassVar[int]
        character_id: int
        character_name: str
        mood_smiley_id: int
        status: _common_pb2.CharacterStatus
        def __init__(self, character_id: _Optional[int] = ..., character_name: _Optional[str] = ..., mood_smiley_id: _Optional[int] = ..., status: _Optional[_Union[_common_pb2.CharacterStatus, _Mapping]] = ...) -> None: ...
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_TAG_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    ONLINE_FIELD_NUMBER: _ClassVar[int]
    account_id: int
    account_tag: _common_pb2.AccountTag
    state: _common_pb2.CharacterState
    online: AcquaintanceInformation.OnlineInformation
    def __init__(self, account_id: _Optional[int] = ..., account_tag: _Optional[_Union[_common_pb2.AccountTag, _Mapping]] = ..., state: _Optional[_Union[_common_pb2.CharacterState, str]] = ..., online: _Optional[_Union[AcquaintanceInformation.OnlineInformation, _Mapping]] = ...) -> None: ...

class ContactInformation(_message.Message):
    __slots__ = ("account_id", "account_tag")
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_TAG_FIELD_NUMBER: _ClassVar[int]
    account_id: int
    account_tag: _common_pb2.AccountTag
    def __init__(self, account_id: _Optional[int] = ..., account_tag: _Optional[_Union[_common_pb2.AccountTag, _Mapping]] = ...) -> None: ...
