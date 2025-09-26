from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GuildMissionActivityTierUpdateRequest(_message.Message):
    __slots__ = ("activity_tier",)
    ACTIVITY_TIER_FIELD_NUMBER: _ClassVar[int]
    activity_tier: int
    def __init__(self, activity_tier: _Optional[int] = ...) -> None: ...

class GuildMissionInformation(_message.Message):
    __slots__ = ("tier", "tier_experience", "guildaton_max", "guildaton", "activity_tier")
    TIER_FIELD_NUMBER: _ClassVar[int]
    TIER_EXPERIENCE_FIELD_NUMBER: _ClassVar[int]
    GUILDATON_MAX_FIELD_NUMBER: _ClassVar[int]
    GUILDATON_FIELD_NUMBER: _ClassVar[int]
    ACTIVITY_TIER_FIELD_NUMBER: _ClassVar[int]
    tier: int
    tier_experience: int
    guildaton_max: int
    guildaton: int
    activity_tier: int
    def __init__(self, tier: _Optional[int] = ..., tier_experience: _Optional[int] = ..., guildaton_max: _Optional[int] = ..., guildaton: _Optional[int] = ..., activity_tier: _Optional[int] = ...) -> None: ...

class GuildMissionInformationUpdateEvent(_message.Message):
    __slots__ = ("unknown_four_hundred_eighty_six",)
    UNKNOWN_FOUR_HUNDRED_EIGHTY_SIX_FIELD_NUMBER: _ClassVar[int]
    unknown_four_hundred_eighty_six: GuildMissionInformation
    def __init__(self, unknown_four_hundred_eighty_six: _Optional[_Union[GuildMissionInformation, _Mapping]] = ...) -> None: ...

class GuildMissionStatusEvent(_message.Message):
    __slots__ = ("disabled", "available", "unavailable")
    class GuildMissionStatusAvailable(_message.Message):
        __slots__ = ("information",)
        INFORMATION_FIELD_NUMBER: _ClassVar[int]
        information: GuildMissionInformation
        def __init__(self, information: _Optional[_Union[GuildMissionInformation, _Mapping]] = ...) -> None: ...
    class GuildMissionStatusDisabled(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class GuildMissionStatusUnavailable(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    DISABLED_FIELD_NUMBER: _ClassVar[int]
    AVAILABLE_FIELD_NUMBER: _ClassVar[int]
    UNAVAILABLE_FIELD_NUMBER: _ClassVar[int]
    disabled: GuildMissionStatusEvent.GuildMissionStatusDisabled
    available: GuildMissionStatusEvent.GuildMissionStatusAvailable
    unavailable: GuildMissionStatusEvent.GuildMissionStatusUnavailable
    def __init__(self, disabled: _Optional[_Union[GuildMissionStatusEvent.GuildMissionStatusDisabled, _Mapping]] = ..., available: _Optional[_Union[GuildMissionStatusEvent.GuildMissionStatusAvailable, _Mapping]] = ..., unavailable: _Optional[_Union[GuildMissionStatusEvent.GuildMissionStatusUnavailable, _Mapping]] = ...) -> None: ...

class GuildMissionStatusRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ServerMaintenanceEvent(_message.Message):
    __slots__ = ("maintenance_date",)
    MAINTENANCE_DATE_FIELD_NUMBER: _ClassVar[int]
    maintenance_date: str
    def __init__(self, maintenance_date: _Optional[str] = ...) -> None: ...

class ServerMaintenanceInformationRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
