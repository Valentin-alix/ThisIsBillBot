import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AccountInformationUpdateEvent(_message.Message):
    __slots__ = ("subscription_end_date",)
    SUBSCRIPTION_END_DATE_FIELD_NUMBER: _ClassVar[int]
    subscription_end_date: int
    def __init__(self, subscription_end_date: _Optional[int] = ...) -> None: ...

class AccountSubscriptionElapsedDurationUpdateEvent(_message.Message):
    __slots__ = ("subscription_elapsed_duration",)
    SUBSCRIPTION_ELAPSED_DURATION_FIELD_NUMBER: _ClassVar[int]
    subscription_elapsed_duration: int
    def __init__(self, subscription_elapsed_duration: _Optional[int] = ...) -> None: ...

class AccountCapabilitiesEvent(_message.Message):
    __slots__ = ("account_id", "tutorial_available", "status", "can_create_new_character")
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    TUTORIAL_AVAILABLE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CAN_CREATE_NEW_CHARACTER_FIELD_NUMBER: _ClassVar[int]
    account_id: int
    tutorial_available: bool
    status: _common_pb2.Hierarchy
    can_create_new_character: bool
    def __init__(self, account_id: _Optional[int] = ..., tutorial_available: bool = ..., status: _Optional[_Union[_common_pb2.Hierarchy, str]] = ..., can_create_new_character: bool = ...) -> None: ...

class AccountAdditionalFacesEvent(_message.Message):
    __slots__ = ("faces",)
    FACES_FIELD_NUMBER: _ClassVar[int]
    faces: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, faces: _Optional[_Iterable[int]] = ...) -> None: ...

class GuestLimitationEvent(_message.Message):
    __slots__ = ("reason",)
    class GuestLimitation(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        LIMITED_TO_REGISTERED: _ClassVar[GuestLimitationEvent.GuestLimitation]
        LIMIT_ON_JOB_XP: _ClassVar[GuestLimitationEvent.GuestLimitation]
        LIMIT_ON_JOB_USE: _ClassVar[GuestLimitationEvent.GuestLimitation]
        LIMIT_ON_MAP: _ClassVar[GuestLimitationEvent.GuestLimitation]
        LIMIT_ON_ITEM: _ClassVar[GuestLimitationEvent.GuestLimitation]
        LIMIT_ON_CHAT: _ClassVar[GuestLimitationEvent.GuestLimitation]
        LIMIT_ON_GUILD: _ClassVar[GuestLimitationEvent.GuestLimitation]
    LIMITED_TO_REGISTERED: GuestLimitationEvent.GuestLimitation
    LIMIT_ON_JOB_XP: GuestLimitationEvent.GuestLimitation
    LIMIT_ON_JOB_USE: GuestLimitationEvent.GuestLimitation
    LIMIT_ON_MAP: GuestLimitationEvent.GuestLimitation
    LIMIT_ON_ITEM: GuestLimitationEvent.GuestLimitation
    LIMIT_ON_CHAT: GuestLimitationEvent.GuestLimitation
    LIMIT_ON_GUILD: GuestLimitationEvent.GuestLimitation
    REASON_FIELD_NUMBER: _ClassVar[int]
    reason: GuestLimitationEvent.GuestLimitation
    def __init__(self, reason: _Optional[_Union[GuestLimitationEvent.GuestLimitation, str]] = ...) -> None: ...

class GuestModeEvent(_message.Message):
    __slots__ = ("effective",)
    EFFECTIVE_FIELD_NUMBER: _ClassVar[int]
    effective: bool
    def __init__(self, effective: bool = ...) -> None: ...

class SubscriptionLimitationEvent(_message.Message):
    __slots__ = ("reason",)
    class SubscriptionRequired(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        LIMITED_TO_SUBSCRIBER: _ClassVar[SubscriptionLimitationEvent.SubscriptionRequired]
        LIMIT_ON_JOB_XP: _ClassVar[SubscriptionLimitationEvent.SubscriptionRequired]
        LIMIT_ON_JOB_USE: _ClassVar[SubscriptionLimitationEvent.SubscriptionRequired]
        LIMIT_ON_MAP: _ClassVar[SubscriptionLimitationEvent.SubscriptionRequired]
        LIMIT_ON_ITEM: _ClassVar[SubscriptionLimitationEvent.SubscriptionRequired]
        LIMIT_ON_HAVEN_BAG: _ClassVar[SubscriptionLimitationEvent.SubscriptionRequired]
    LIMITED_TO_SUBSCRIBER: SubscriptionLimitationEvent.SubscriptionRequired
    LIMIT_ON_JOB_XP: SubscriptionLimitationEvent.SubscriptionRequired
    LIMIT_ON_JOB_USE: SubscriptionLimitationEvent.SubscriptionRequired
    LIMIT_ON_MAP: SubscriptionLimitationEvent.SubscriptionRequired
    LIMIT_ON_ITEM: SubscriptionLimitationEvent.SubscriptionRequired
    LIMIT_ON_HAVEN_BAG: SubscriptionLimitationEvent.SubscriptionRequired
    REASON_FIELD_NUMBER: _ClassVar[int]
    reason: SubscriptionLimitationEvent.SubscriptionRequired
    def __init__(self, reason: _Optional[_Union[SubscriptionLimitationEvent.SubscriptionRequired, str]] = ...) -> None: ...

class SubscriptionZoneEvent(_message.Message):
    __slots__ = ("effective",)
    EFFECTIVE_FIELD_NUMBER: _ClassVar[int]
    effective: bool
    def __init__(self, effective: bool = ...) -> None: ...

class AccountRoleStatusEvent(_message.Message):
    __slots__ = ("unknown_two", "unknown_three", "role")
    class UnknownTwo(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN_TWO_UNSPECIFIED: _ClassVar[AccountRoleStatusEvent.UnknownTwo]
    UNKNOWN_TWO_UNSPECIFIED: AccountRoleStatusEvent.UnknownTwo
    UNKNOWN_TWO_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_THREE_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    unknown_two: AccountRoleStatusEvent.UnknownTwo
    unknown_three: bool
    role: _common_pb2.Hierarchy
    def __init__(self, unknown_two: _Optional[_Union[AccountRoleStatusEvent.UnknownTwo, str]] = ..., unknown_three: bool = ..., role: _Optional[_Union[_common_pb2.Hierarchy, str]] = ...) -> None: ...

class AccountSecurityFlagsEvent(_message.Message):
    __slots__ = ("security_flags",)
    class SecurityFlags(_message.Message):
        __slots__ = ("unknown_four", "unknown_five", "unknown_six")
        UNKNOWN_FOUR_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FIVE_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_SIX_FIELD_NUMBER: _ClassVar[int]
        unknown_four: bool
        unknown_five: bool
        unknown_six: bool
        def __init__(self, unknown_four: bool = ..., unknown_five: bool = ..., unknown_six: bool = ...) -> None: ...
    SECURITY_FLAGS_FIELD_NUMBER: _ClassVar[int]
    security_flags: AccountSecurityFlagsEvent.SecurityFlags
    def __init__(self, security_flags: _Optional[_Union[AccountSecurityFlagsEvent.SecurityFlags, _Mapping]] = ...) -> None: ...

class SessionElapsedDurationEvent(_message.Message):
    __slots__ = ("duration_seconds",)
    DURATION_SECONDS_FIELD_NUMBER: _ClassVar[int]
    duration_seconds: int
    def __init__(self, duration_seconds: _Optional[int] = ...) -> None: ...
