import game_message_pb2 as _game_message_pb2
import report_pb2 as _report_pb2
import ladder_pb2 as _ladder_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ExperienceLadderPageRequest(_message.Message):
    __slots__ = ("unknown_fqqg", "server_id")
    UNKNOWN_FQQG_FIELD_NUMBER: _ClassVar[int]
    SERVER_ID_FIELD_NUMBER: _ClassVar[int]
    unknown_fqqg: _containers.RepeatedScalarFieldContainer[bool]
    server_id: int
    def __init__(self, unknown_fqqg: _Optional[_Iterable[bool]] = ..., server_id: _Optional[int] = ...) -> None: ...

class ExperienceLadderSelfRankRequest(_message.Message):
    __slots__ = ("server_id",)
    SERVER_ID_FIELD_NUMBER: _ClassVar[int]
    server_id: int
    def __init__(self, server_id: _Optional[int] = ...) -> None: ...

class ExperienceLadderEntry(_message.Message):
    __slots__ = ("experience", "character", "rank")
    EXPERIENCE_FIELD_NUMBER: _ClassVar[int]
    CHARACTER_FIELD_NUMBER: _ClassVar[int]
    RANK_FIELD_NUMBER: _ClassVar[int]
    experience: int
    character: _ladder_pb2.LadderCharacter
    rank: int
    def __init__(self, experience: _Optional[int] = ..., character: _Optional[_Union[_ladder_pb2.LadderCharacter, _Mapping]] = ..., rank: _Optional[int] = ...) -> None: ...

class ExperienceLadderPageEvent(_message.Message):
    __slots__ = ("entries",)
    ENTRIES_FIELD_NUMBER: _ClassVar[int]
    entries: _containers.RepeatedCompositeFieldContainer[ExperienceLadderEntry]
    def __init__(self, entries: _Optional[_Iterable[_Union[ExperienceLadderEntry, _Mapping]]] = ...) -> None: ...

class UnknownIqd(_message.Message):
    __slots__ = ("unknown_fqrc", "unknown_fqrd")
    UNKNOWN_FQRC_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FQRD_FIELD_NUMBER: _ClassVar[int]
    unknown_fqrc: str
    unknown_fqrd: int
    def __init__(self, unknown_fqrc: _Optional[str] = ..., unknown_fqrd: _Optional[int] = ...) -> None: ...

class UnknownIqg(_message.Message):
    __slots__ = ("entries",)
    ENTRIES_FIELD_NUMBER: _ClassVar[int]
    entries: _containers.RepeatedCompositeFieldContainer[ExperienceLadderEntry]
    def __init__(self, entries: _Optional[_Iterable[_Union[ExperienceLadderEntry, _Mapping]]] = ...) -> None: ...

class ExperienceLadderSelfRankEvent(_message.Message):
    __slots__ = ("entry",)
    ENTRY_FIELD_NUMBER: _ClassVar[int]
    entry: ExperienceLadderEntry
    def __init__(self, entry: _Optional[_Union[ExperienceLadderEntry, _Mapping]] = ...) -> None: ...

class GuildTokenConfiguration(_message.Message):
    __slots__ = ("guild_token_items", "refresh_interval_milliseconds", "thresholds")
    class GuildTokenThresholds(_message.Message):
        __slots__ = ("unknown_fytt", "unknown_fytu", "unknown_fytv", "unknown_fytw")
        UNKNOWN_FYTT_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FYTU_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FYTV_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FYTW_FIELD_NUMBER: _ClassVar[int]
        unknown_fytt: int
        unknown_fytu: int
        unknown_fytv: int
        unknown_fytw: int
        def __init__(self, unknown_fytt: _Optional[int] = ..., unknown_fytu: _Optional[int] = ..., unknown_fytv: _Optional[int] = ..., unknown_fytw: _Optional[int] = ...) -> None: ...
    class GuildTokenItems(_message.Message):
        __slots__ = ("guildaton_item_id", "unknown_fyul", "unknown_fyum", "unknown_fyun", "guild_token_item_id", "unknown_fyup")
        GUILDATON_ITEM_ID_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FYUL_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FYUM_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FYUN_FIELD_NUMBER: _ClassVar[int]
        GUILD_TOKEN_ITEM_ID_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FYUP_FIELD_NUMBER: _ClassVar[int]
        guildaton_item_id: int
        unknown_fyul: int
        unknown_fyum: int
        unknown_fyun: int
        guild_token_item_id: int
        unknown_fyup: int
        def __init__(self, guildaton_item_id: _Optional[int] = ..., unknown_fyul: _Optional[int] = ..., unknown_fyum: _Optional[int] = ..., unknown_fyun: _Optional[int] = ..., guild_token_item_id: _Optional[int] = ..., unknown_fyup: _Optional[int] = ...) -> None: ...
    GUILD_TOKEN_ITEMS_FIELD_NUMBER: _ClassVar[int]
    REFRESH_INTERVAL_MILLISECONDS_FIELD_NUMBER: _ClassVar[int]
    THRESHOLDS_FIELD_NUMBER: _ClassVar[int]
    guild_token_items: GuildTokenConfiguration.GuildTokenItems
    refresh_interval_milliseconds: int
    thresholds: GuildTokenConfiguration.GuildTokenThresholds
    def __init__(self, guild_token_items: _Optional[_Union[GuildTokenConfiguration.GuildTokenItems, _Mapping]] = ..., refresh_interval_milliseconds: _Optional[int] = ..., thresholds: _Optional[_Union[GuildTokenConfiguration.GuildTokenThresholds, _Mapping]] = ...) -> None: ...

class GuildTokenConfigurationEvent(_message.Message):
    __slots__ = ("configuration",)
    CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    configuration: GuildTokenConfiguration
    def __init__(self, configuration: _Optional[_Union[GuildTokenConfiguration, _Mapping]] = ...) -> None: ...
