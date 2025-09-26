from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GuildMissionTierDetailEvent(_message.Message):
    __slots__ = ("failure", "success")
    class GuildMissionTierDetailFailure(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class GuildMissionTierDetailUnknownResult(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class GuildMissionTierDetailSuccess(_message.Message):
        __slots__ = ("disabled_entries",)
        DISABLED_ENTRIES_FIELD_NUMBER: _ClassVar[int]
        disabled_entries: GuildMissionDisabledEntries
        def __init__(self, disabled_entries: _Optional[_Union[GuildMissionDisabledEntries, _Mapping]] = ...) -> None: ...
    FAILURE_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    failure: GuildMissionTierDetailEvent.GuildMissionTierDetailFailure
    success: GuildMissionTierDetailEvent.GuildMissionTierDetailSuccess
    def __init__(self, failure: _Optional[_Union[GuildMissionTierDetailEvent.GuildMissionTierDetailFailure, _Mapping]] = ..., success: _Optional[_Union[GuildMissionTierDetailEvent.GuildMissionTierDetailSuccess, _Mapping]] = ...) -> None: ...

class GuildMissionTierDetailRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GuildMissionDisabledEntries(_message.Message):
    __slots__ = ("disabled_categories", "disabled_tiers")
    DISABLED_CATEGORIES_FIELD_NUMBER: _ClassVar[int]
    DISABLED_TIERS_FIELD_NUMBER: _ClassVar[int]
    disabled_categories: _containers.RepeatedScalarFieldContainer[int]
    disabled_tiers: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, disabled_categories: _Optional[_Iterable[int]] = ..., disabled_tiers: _Optional[_Iterable[int]] = ...) -> None: ...

class GuildMissionUpdateEvent(_message.Message):
    __slots__ = ("failure", "success")
    class GuildMissionUpdateFailure(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class GuildMissionUpdateSuccess(_message.Message):
        __slots__ = ("disabled_entries",)
        DISABLED_ENTRIES_FIELD_NUMBER: _ClassVar[int]
        disabled_entries: GuildMissionDisabledEntries
        def __init__(self, disabled_entries: _Optional[_Union[GuildMissionDisabledEntries, _Mapping]] = ...) -> None: ...
    FAILURE_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    failure: GuildMissionUpdateEvent.GuildMissionUpdateFailure
    success: GuildMissionUpdateEvent.GuildMissionUpdateSuccess
    def __init__(self, failure: _Optional[_Union[GuildMissionUpdateEvent.GuildMissionUpdateFailure, _Mapping]] = ..., success: _Optional[_Union[GuildMissionUpdateEvent.GuildMissionUpdateSuccess, _Mapping]] = ...) -> None: ...

class GuildMissionUpdateRequest(_message.Message):
    __slots__ = ("disabled_entries",)
    class GuildMissionUpdateMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        GUILD_MISSION_UPDATE_MODE_UNSPECIFIED: _ClassVar[GuildMissionUpdateRequest.GuildMissionUpdateMode]
        GUILD_MISSION_UPDATE_MODE_UNKNOWN: _ClassVar[GuildMissionUpdateRequest.GuildMissionUpdateMode]
    GUILD_MISSION_UPDATE_MODE_UNSPECIFIED: GuildMissionUpdateRequest.GuildMissionUpdateMode
    GUILD_MISSION_UPDATE_MODE_UNKNOWN: GuildMissionUpdateRequest.GuildMissionUpdateMode
    DISABLED_ENTRIES_FIELD_NUMBER: _ClassVar[int]
    disabled_entries: GuildMissionDisabledEntries
    def __init__(self, disabled_entries: _Optional[_Union[GuildMissionDisabledEntries, _Mapping]] = ...) -> None: ...
