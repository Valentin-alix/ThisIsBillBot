import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Channel(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    GLOBAL: _ClassVar[Channel]
    TEAM: _ClassVar[Channel]
    GUILD: _ClassVar[Channel]
    ALLIANCE: _ClassVar[Channel]
    PARTY: _ClassVar[Channel]
    SALES: _ClassVar[Channel]
    SEEK: _ClassVar[Channel]
    NOOB: _ClassVar[Channel]
    ADMIN: _ClassVar[Channel]
    ARENA: _ClassVar[Channel]
    PRIVATE: _ClassVar[Channel]
    COMMUNAUTY: _ClassVar[Channel]
    INFO: _ClassVar[Channel]
    FIGHT_LOG: _ClassVar[Channel]
    ADS: _ClassVar[Channel]
    EVENT: _ClassVar[Channel]
    EXCHANGE: _ClassVar[Channel]
    TERRITORY: _ClassVar[Channel]
    GUILD_RAID: _ClassVar[Channel]
    JESAISPAS: _ClassVar[Channel]
GLOBAL: Channel
TEAM: Channel
GUILD: Channel
ALLIANCE: Channel
PARTY: Channel
SALES: Channel
SEEK: Channel
NOOB: Channel
ADMIN: Channel
ARENA: Channel
PRIVATE: Channel
COMMUNAUTY: Channel
INFO: Channel
FIGHT_LOG: Channel
ADS: Channel
EVENT: Channel
EXCHANGE: Channel
TERRITORY: Channel
GUILD_RAID: Channel
JESAISPAS: Channel

class ChatMessageLinks(_message.Message):
    __slots__ = ("objects", "unknown_fzsv")
    OBJECTS_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FZSV_FIELD_NUMBER: _ClassVar[int]
    objects: _containers.RepeatedCompositeFieldContainer[_common_pb2.ObjectItem]
    unknown_fzsv: _containers.RepeatedCompositeFieldContainer[UnknownKsu]
    def __init__(self, objects: _Optional[_Iterable[_Union[_common_pb2.ObjectItem, _Mapping]]] = ..., unknown_fzsv: _Optional[_Iterable[_Union[UnknownKsu, _Mapping]]] = ...) -> None: ...

class UnknownKsu(_message.Message):
    __slots__ = ("unknown_fztj", "unknown_fztk", "unknown_fztl", "unknown_fztm", "unknown_fztn", "unknown_fzto", "unknown_fztp")
    UNKNOWN_FZTJ_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FZTK_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FZTL_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FZTM_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FZTN_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FZTO_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FZTP_FIELD_NUMBER: _ClassVar[int]
    unknown_fztj: int
    unknown_fztk: _common_pb2.MapCoordinates
    unknown_fztl: str
    unknown_fztm: int
    unknown_fztn: int
    unknown_fzto: int
    unknown_fztp: int
    def __init__(self, unknown_fztj: _Optional[int] = ..., unknown_fztk: _Optional[_Union[_common_pb2.MapCoordinates, _Mapping]] = ..., unknown_fztl: _Optional[str] = ..., unknown_fztm: _Optional[int] = ..., unknown_fztn: _Optional[int] = ..., unknown_fzto: _Optional[int] = ..., unknown_fztp: _Optional[int] = ...) -> None: ...

class ChatPrivateMessageRequest(_message.Message):
    __slots__ = ("content", "links", "name", "tag")
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    LINKS_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TAG_FIELD_NUMBER: _ClassVar[int]
    content: str
    links: ChatMessageLinks
    name: str
    tag: _common_pb2.AccountTag
    def __init__(self, content: _Optional[str] = ..., links: _Optional[_Union[ChatMessageLinks, _Mapping]] = ..., name: _Optional[str] = ..., tag: _Optional[_Union[_common_pb2.AccountTag, _Mapping]] = ...) -> None: ...

class ChatPrivateCopyMessageEvent(_message.Message):
    __slots__ = ("content", "date", "target_character_id", "target_name", "object")
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    TARGET_CHARACTER_ID_FIELD_NUMBER: _ClassVar[int]
    TARGET_NAME_FIELD_NUMBER: _ClassVar[int]
    OBJECT_FIELD_NUMBER: _ClassVar[int]
    content: str
    date: str
    target_character_id: int
    target_name: str
    object: _containers.RepeatedCompositeFieldContainer[_common_pb2.ObjectItemInventory]
    def __init__(self, content: _Optional[str] = ..., date: _Optional[str] = ..., target_character_id: _Optional[int] = ..., target_name: _Optional[str] = ..., object: _Optional[_Iterable[_Union[_common_pb2.ObjectItemInventory, _Mapping]]] = ...) -> None: ...

class ChatChannelMessageRequest(_message.Message):
    __slots__ = ("content", "channel", "links")
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    CHANNEL_FIELD_NUMBER: _ClassVar[int]
    LINKS_FIELD_NUMBER: _ClassVar[int]
    content: str
    channel: Channel
    links: ChatMessageLinks
    def __init__(self, content: _Optional[str] = ..., channel: _Optional[_Union[Channel, str]] = ..., links: _Optional[_Union[ChatMessageLinks, _Mapping]] = ...) -> None: ...

class ChatChannelMessageEvent(_message.Message):
    __slots__ = ("content", "channel", "date", "sender_character_id", "sender_account_id", "sender_prefix", "sender_name", "from_admin", "links", "origin_server_id")
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    CHANNEL_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    SENDER_CHARACTER_ID_FIELD_NUMBER: _ClassVar[int]
    SENDER_ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    SENDER_PREFIX_FIELD_NUMBER: _ClassVar[int]
    SENDER_NAME_FIELD_NUMBER: _ClassVar[int]
    FROM_ADMIN_FIELD_NUMBER: _ClassVar[int]
    LINKS_FIELD_NUMBER: _ClassVar[int]
    ORIGIN_SERVER_ID_FIELD_NUMBER: _ClassVar[int]
    content: str
    channel: Channel
    date: str
    sender_character_id: int
    sender_account_id: int
    sender_prefix: str
    sender_name: str
    from_admin: bool
    links: ChatMessageLinks
    origin_server_id: int
    def __init__(self, content: _Optional[str] = ..., channel: _Optional[_Union[Channel, str]] = ..., date: _Optional[str] = ..., sender_character_id: _Optional[int] = ..., sender_account_id: _Optional[int] = ..., sender_prefix: _Optional[str] = ..., sender_name: _Optional[str] = ..., from_admin: bool = ..., links: _Optional[_Union[ChatMessageLinks, _Mapping]] = ..., origin_server_id: _Optional[int] = ...) -> None: ...

class ChatErrorEvent(_message.Message):
    __slots__ = ("error",)
    class Error(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN: _ClassVar[ChatErrorEvent.Error]
        RECEIVER_NOT_FOUND: _ClassVar[ChatErrorEvent.Error]
        INTERIOR_MONOLOGUE: _ClassVar[ChatErrorEvent.Error]
        NO_GUILD: _ClassVar[ChatErrorEvent.Error]
        NO_PARTY: _ClassVar[ChatErrorEvent.Error]
        ALLIANCE: _ClassVar[ChatErrorEvent.Error]
        INVALID_MAP: _ClassVar[ChatErrorEvent.Error]
        NO_PARTY_ARENA: _ClassVar[ChatErrorEvent.Error]
        NO_TEAM: _ClassVar[ChatErrorEvent.Error]
        MALFORMED_CONTENT: _ClassVar[ChatErrorEvent.Error]
        NO_EXCHANGE: _ClassVar[ChatErrorEvent.Error]
    UNKNOWN: ChatErrorEvent.Error
    RECEIVER_NOT_FOUND: ChatErrorEvent.Error
    INTERIOR_MONOLOGUE: ChatErrorEvent.Error
    NO_GUILD: ChatErrorEvent.Error
    NO_PARTY: ChatErrorEvent.Error
    ALLIANCE: ChatErrorEvent.Error
    INVALID_MAP: ChatErrorEvent.Error
    NO_PARTY_ARENA: ChatErrorEvent.Error
    NO_TEAM: ChatErrorEvent.Error
    MALFORMED_CONTENT: ChatErrorEvent.Error
    NO_EXCHANGE: ChatErrorEvent.Error
    ERROR_FIELD_NUMBER: _ClassVar[int]
    error: ChatErrorEvent.Error
    def __init__(self, error: _Optional[_Union[ChatErrorEvent.Error, str]] = ...) -> None: ...

class SubscribeMultipleChannelRequest(_message.Message):
    __slots__ = ("channel_enabled", "channel_disabled")
    CHANNEL_ENABLED_FIELD_NUMBER: _ClassVar[int]
    CHANNEL_DISABLED_FIELD_NUMBER: _ClassVar[int]
    channel_enabled: _containers.RepeatedScalarFieldContainer[Channel]
    channel_disabled: _containers.RepeatedScalarFieldContainer[Channel]
    def __init__(self, channel_enabled: _Optional[_Iterable[_Union[Channel, str]]] = ..., channel_disabled: _Optional[_Iterable[_Union[Channel, str]]] = ...) -> None: ...

class ChannelUpdateEvent(_message.Message):
    __slots__ = ("channel", "enable")
    CHANNEL_FIELD_NUMBER: _ClassVar[int]
    ENABLE_FIELD_NUMBER: _ClassVar[int]
    channel: Channel
    enable: bool
    def __init__(self, channel: _Optional[_Union[Channel, str]] = ..., enable: bool = ...) -> None: ...

class ChatChannelsEnabledEvent(_message.Message):
    __slots__ = ("active_channels", "disabled_channels")
    ACTIVE_CHANNELS_FIELD_NUMBER: _ClassVar[int]
    DISABLED_CHANNELS_FIELD_NUMBER: _ClassVar[int]
    active_channels: _containers.RepeatedScalarFieldContainer[Channel]
    disabled_channels: _containers.RepeatedScalarFieldContainer[Channel]
    def __init__(self, active_channels: _Optional[_Iterable[_Union[Channel, str]]] = ..., disabled_channels: _Optional[_Iterable[_Union[Channel, str]]] = ...) -> None: ...
