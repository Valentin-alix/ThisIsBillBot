from com.ankama.dofus.server.game.protocol import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GuildApplicationSubmitRequest(_message.Message):
    __slots__ = ("apply_text", "guild_id", "time_spent", "language_filter", "ambiance_filter", "play_time_filter", "interest_filter", "min_max_guild_level_filter", "recruitment_type_filter", "min_max_character_level_filter", "min_max_achievement_filter", "search_name_filter", "last_sort_filter")
    APPLY_TEXT_FIELD_NUMBER: _ClassVar[int]
    GUILD_ID_FIELD_NUMBER: _ClassVar[int]
    TIME_SPENT_FIELD_NUMBER: _ClassVar[int]
    LANGUAGE_FILTER_FIELD_NUMBER: _ClassVar[int]
    AMBIANCE_FILTER_FIELD_NUMBER: _ClassVar[int]
    PLAY_TIME_FILTER_FIELD_NUMBER: _ClassVar[int]
    INTEREST_FILTER_FIELD_NUMBER: _ClassVar[int]
    MIN_MAX_GUILD_LEVEL_FILTER_FIELD_NUMBER: _ClassVar[int]
    RECRUITMENT_TYPE_FILTER_FIELD_NUMBER: _ClassVar[int]
    MIN_MAX_CHARACTER_LEVEL_FILTER_FIELD_NUMBER: _ClassVar[int]
    MIN_MAX_ACHIEVEMENT_FILTER_FIELD_NUMBER: _ClassVar[int]
    SEARCH_NAME_FILTER_FIELD_NUMBER: _ClassVar[int]
    LAST_SORT_FILTER_FIELD_NUMBER: _ClassVar[int]
    apply_text: str
    guild_id: int
    time_spent: int
    language_filter: str
    ambiance_filter: str
    play_time_filter: str
    interest_filter: str
    min_max_guild_level_filter: str
    recruitment_type_filter: str
    min_max_character_level_filter: str
    min_max_achievement_filter: str
    search_name_filter: str
    last_sort_filter: str
    def __init__(self, apply_text: _Optional[str] = ..., guild_id: _Optional[int] = ..., time_spent: _Optional[int] = ..., language_filter: _Optional[str] = ..., ambiance_filter: _Optional[str] = ..., play_time_filter: _Optional[str] = ..., interest_filter: _Optional[str] = ..., min_max_guild_level_filter: _Optional[str] = ..., recruitment_type_filter: _Optional[str] = ..., min_max_character_level_filter: _Optional[str] = ..., min_max_achievement_filter: _Optional[str] = ..., search_name_filter: _Optional[str] = ..., last_sort_filter: _Optional[str] = ...) -> None: ...

class GuildApplicationUpdateRequest(_message.Message):
    __slots__ = ("apply_text", "guild_id")
    APPLY_TEXT_FIELD_NUMBER: _ClassVar[int]
    GUILD_ID_FIELD_NUMBER: _ClassVar[int]
    apply_text: str
    guild_id: int
    def __init__(self, apply_text: _Optional[str] = ..., guild_id: _Optional[int] = ...) -> None: ...

class GuildApplicationDeleteRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GuildApplicationListenRequest(_message.Message):
    __slots__ = ("listen",)
    LISTEN_FIELD_NUMBER: _ClassVar[int]
    listen: bool
    def __init__(self, listen: bool = ...) -> None: ...

class GuildApplicationGetOwnRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GuildApplicationsRequest(_message.Message):
    __slots__ = ("offset", "count")
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    offset: int
    count: int
    def __init__(self, offset: _Optional[int] = ..., count: _Optional[int] = ...) -> None: ...

class GuildApplicationAnswerRequest(_message.Message):
    __slots__ = ("accepted", "player_id")
    ACCEPTED_FIELD_NUMBER: _ClassVar[int]
    PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
    accepted: bool
    player_id: int
    def __init__(self, accepted: bool = ..., player_id: _Optional[int] = ...) -> None: ...

class GuildApplicationPresenceRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GuildApplicationDeletedEvent(_message.Message):
    __slots__ = ("deleted",)
    DELETED_FIELD_NUMBER: _ClassVar[int]
    deleted: bool
    def __init__(self, deleted: bool = ...) -> None: ...

class GuildApplicationPlayerEvent(_message.Message):
    __slots__ = ("application",)
    class ApplicationInformation(_message.Message):
        __slots__ = ("guild_information", "apply")
        GUILD_INFORMATION_FIELD_NUMBER: _ClassVar[int]
        APPLY_FIELD_NUMBER: _ClassVar[int]
        guild_information: _common_pb2.GuildInformation
        apply: _common_pb2.SocialApplicationInformation
        def __init__(self, guild_information: _Optional[_Union[_common_pb2.GuildInformation, _Mapping]] = ..., apply: _Optional[_Union[_common_pb2.SocialApplicationInformation, _Mapping]] = ...) -> None: ...
    APPLICATION_FIELD_NUMBER: _ClassVar[int]
    application: GuildApplicationPlayerEvent.ApplicationInformation
    def __init__(self, application: _Optional[_Union[GuildApplicationPlayerEvent.ApplicationInformation, _Mapping]] = ...) -> None: ...

class GuildApplicationAnswerEvent(_message.Message):
    __slots__ = ("accepted", "guild_information")
    ACCEPTED_FIELD_NUMBER: _ClassVar[int]
    GUILD_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    accepted: bool
    guild_information: _common_pb2.GuildInformation
    def __init__(self, accepted: bool = ..., guild_information: _Optional[_Union[_common_pb2.GuildInformation, _Mapping]] = ...) -> None: ...

class GuildApplicationsEvent(_message.Message):
    __slots__ = ("offset", "count", "total", "applies")
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    APPLIES_FIELD_NUMBER: _ClassVar[int]
    offset: int
    count: int
    total: int
    applies: _containers.RepeatedCompositeFieldContainer[_common_pb2.SocialApplicationInformation]
    def __init__(self, offset: _Optional[int] = ..., count: _Optional[int] = ..., total: _Optional[int] = ..., applies: _Optional[_Iterable[_Union[_common_pb2.SocialApplicationInformation, _Mapping]]] = ...) -> None: ...

class GuildApplicationModifiedEvent(_message.Message):
    __slots__ = ("application", "state", "player_id")
    APPLICATION_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
    application: _common_pb2.SocialApplicationInformation
    state: _common_pb2.SocialApplicationState
    player_id: int
    def __init__(self, application: _Optional[_Union[_common_pb2.SocialApplicationInformation, _Mapping]] = ..., state: _Optional[_Union[_common_pb2.SocialApplicationState, str]] = ..., player_id: _Optional[int] = ...) -> None: ...

class GuildApplicationReceivedEvent(_message.Message):
    __slots__ = ("player_name", "player_id")
    PLAYER_NAME_FIELD_NUMBER: _ClassVar[int]
    PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
    player_name: str
    player_id: int
    def __init__(self, player_name: _Optional[str] = ..., player_id: _Optional[int] = ...) -> None: ...

class GuildApplicationPresenceEvent(_message.Message):
    __slots__ = ("is_application",)
    IS_APPLICATION_FIELD_NUMBER: _ClassVar[int]
    is_application: bool
    def __init__(self, is_application: bool = ...) -> None: ...
