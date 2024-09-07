from com.ankama.dofus.server.game.protocol import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DateRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class WhoAmIRequest(_message.Message):
    __slots__ = ("verbose",)
    VERBOSE_FIELD_NUMBER: _ClassVar[int]
    verbose: bool
    def __init__(self, verbose: bool = ...) -> None: ...

class WhoIsRequest(_message.Message):
    __slots__ = ("verbose", "target")
    VERBOSE_FIELD_NUMBER: _ClassVar[int]
    TARGET_FIELD_NUMBER: _ClassVar[int]
    verbose: bool
    target: _common_pb2.PlayerSearch
    def __init__(self, verbose: bool = ..., target: _Optional[_Union[_common_pb2.PlayerSearch, _Mapping]] = ...) -> None: ...

class WhoIsNumericRequest(_message.Message):
    __slots__ = ("player_id",)
    PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
    player_id: int
    def __init__(self, player_id: _Optional[int] = ...) -> None: ...

class BasicLatencyStatsRequest(_message.Message):
    __slots__ = ("latency",)
    LATENCY_FIELD_NUMBER: _ClassVar[int]
    latency: int
    def __init__(self, latency: _Optional[int] = ...) -> None: ...

class SequenceNumberRequest(_message.Message):
    __slots__ = ("number",)
    NUMBER_FIELD_NUMBER: _ClassVar[int]
    number: int
    def __init__(self, number: _Optional[int] = ...) -> None: ...

class DateEvent(_message.Message):
    __slots__ = ("day", "month", "year")
    DAY_FIELD_NUMBER: _ClassVar[int]
    MONTH_FIELD_NUMBER: _ClassVar[int]
    YEAR_FIELD_NUMBER: _ClassVar[int]
    day: int
    month: int
    year: int
    def __init__(self, day: _Optional[int] = ..., month: _Optional[int] = ..., year: _Optional[int] = ...) -> None: ...

class TimeEvent(_message.Message):
    __slots__ = ("timestamp", "timezone_offset")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    TIMEZONE_OFFSET_FIELD_NUMBER: _ClassVar[int]
    timestamp: int
    timezone_offset: int
    def __init__(self, timestamp: _Optional[int] = ..., timezone_offset: _Optional[int] = ...) -> None: ...

class AlmanachCalendarDateEvent(_message.Message):
    __slots__ = ("date_id",)
    DATE_ID_FIELD_NUMBER: _ClassVar[int]
    date_id: int
    def __init__(self, date_id: _Optional[int] = ...) -> None: ...

class SystemMessageDisplayEvent(_message.Message):
    __slots__ = ("hang_up", "message_id", "parameters")
    HANG_UP_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_ID_FIELD_NUMBER: _ClassVar[int]
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    hang_up: bool
    message_id: int
    parameters: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, hang_up: bool = ..., message_id: _Optional[int] = ..., parameters: _Optional[_Iterable[str]] = ...) -> None: ...

class TextInformationEvent(_message.Message):
    __slots__ = ("message_type", "message_id", "parameters")
    class TextInformationType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TEXT_INFORMATION_MESSAGE: _ClassVar[TextInformationEvent.TextInformationType]
        TEXT_INFORMATION_ERROR: _ClassVar[TextInformationEvent.TextInformationType]
        TEXT_INFORMATION_PVP: _ClassVar[TextInformationEvent.TextInformationType]
        TEXT_INFORMATION_FIGHT_LOG: _ClassVar[TextInformationEvent.TextInformationType]
        TEXT_INFORMATION_POPUP: _ClassVar[TextInformationEvent.TextInformationType]
        TEXT_LIVING_OBJECT: _ClassVar[TextInformationEvent.TextInformationType]
        TEXT_ENTITY_TALK: _ClassVar[TextInformationEvent.TextInformationType]
        TEXT_INFORMATION_FIGHT: _ClassVar[TextInformationEvent.TextInformationType]
        TEXT_INFORMATION_EVENT: _ClassVar[TextInformationEvent.TextInformationType]
    TEXT_INFORMATION_MESSAGE: TextInformationEvent.TextInformationType
    TEXT_INFORMATION_ERROR: TextInformationEvent.TextInformationType
    TEXT_INFORMATION_PVP: TextInformationEvent.TextInformationType
    TEXT_INFORMATION_FIGHT_LOG: TextInformationEvent.TextInformationType
    TEXT_INFORMATION_POPUP: TextInformationEvent.TextInformationType
    TEXT_LIVING_OBJECT: TextInformationEvent.TextInformationType
    TEXT_ENTITY_TALK: TextInformationEvent.TextInformationType
    TEXT_INFORMATION_FIGHT: TextInformationEvent.TextInformationType
    TEXT_INFORMATION_EVENT: TextInformationEvent.TextInformationType
    MESSAGE_TYPE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_ID_FIELD_NUMBER: _ClassVar[int]
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    message_type: TextInformationEvent.TextInformationType
    message_id: int
    parameters: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, message_type: _Optional[_Union[TextInformationEvent.TextInformationType, str]] = ..., message_id: _Optional[int] = ..., parameters: _Optional[_Iterable[str]] = ...) -> None: ...

class WhoIsEvent(_message.Message):
    __slots__ = ("self", "position", "account_name", "account_tag", "account_id", "character_name", "character_id", "area_id", "server_id", "origin_server_id", "guild_information", "alliance_information", "verbose", "state")
    SELF_FIELD_NUMBER: _ClassVar[int]
    POSITION_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_NAME_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_TAG_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    CHARACTER_NAME_FIELD_NUMBER: _ClassVar[int]
    CHARACTER_ID_FIELD_NUMBER: _ClassVar[int]
    AREA_ID_FIELD_NUMBER: _ClassVar[int]
    SERVER_ID_FIELD_NUMBER: _ClassVar[int]
    ORIGIN_SERVER_ID_FIELD_NUMBER: _ClassVar[int]
    GUILD_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    ALLIANCE_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    VERBOSE_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    self: bool
    position: _common_pb2.Hierarchy
    account_name: str
    account_tag: str
    account_id: int
    character_name: str
    character_id: int
    area_id: int
    server_id: int
    origin_server_id: int
    guild_information: _common_pb2.GuildInformation
    alliance_information: _common_pb2.AllianceInformation
    verbose: bool
    state: _common_pb2.CharacterState
    def __init__(self, self_: bool = ..., position: _Optional[_Union[_common_pb2.Hierarchy, str]] = ..., account_name: _Optional[str] = ..., account_tag: _Optional[str] = ..., account_id: _Optional[int] = ..., character_name: _Optional[str] = ..., character_id: _Optional[int] = ..., area_id: _Optional[int] = ..., server_id: _Optional[int] = ..., origin_server_id: _Optional[int] = ..., guild_information: _Optional[_Union[_common_pb2.GuildInformation, _Mapping]] = ..., alliance_information: _Optional[_Union[_common_pb2.AllianceInformation, _Mapping]] = ..., verbose: bool = ..., state: _Optional[_Union[_common_pb2.CharacterState, str]] = ...) -> None: ...

class WhoIsNoMatchEvent(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class WhoIsNumericEvent(_message.Message):
    __slots__ = ("player_id", "account_id")
    PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    player_id: int
    account_id: int
    def __init__(self, player_id: _Optional[int] = ..., account_id: _Optional[int] = ...) -> None: ...

class BasicLatencyStatsEvent(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SequenceNumberEvent(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CurrentServerStatusUpdateEvent(_message.Message):
    __slots__ = ("status",)
    class ServerStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN: _ClassVar[CurrentServerStatusUpdateEvent.ServerStatus]
        OFFLINE: _ClassVar[CurrentServerStatusUpdateEvent.ServerStatus]
        STARTING: _ClassVar[CurrentServerStatusUpdateEvent.ServerStatus]
        ONLINE: _ClassVar[CurrentServerStatusUpdateEvent.ServerStatus]
        NO_JOIN: _ClassVar[CurrentServerStatusUpdateEvent.ServerStatus]
        SAVING: _ClassVar[CurrentServerStatusUpdateEvent.ServerStatus]
        STOPPING: _ClassVar[CurrentServerStatusUpdateEvent.ServerStatus]
        FULL: _ClassVar[CurrentServerStatusUpdateEvent.ServerStatus]
    UNKNOWN: CurrentServerStatusUpdateEvent.ServerStatus
    OFFLINE: CurrentServerStatusUpdateEvent.ServerStatus
    STARTING: CurrentServerStatusUpdateEvent.ServerStatus
    ONLINE: CurrentServerStatusUpdateEvent.ServerStatus
    NO_JOIN: CurrentServerStatusUpdateEvent.ServerStatus
    SAVING: CurrentServerStatusUpdateEvent.ServerStatus
    STOPPING: CurrentServerStatusUpdateEvent.ServerStatus
    FULL: CurrentServerStatusUpdateEvent.ServerStatus
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: CurrentServerStatusUpdateEvent.ServerStatus
    def __init__(self, status: _Optional[_Union[CurrentServerStatusUpdateEvent.ServerStatus, str]] = ...) -> None: ...
