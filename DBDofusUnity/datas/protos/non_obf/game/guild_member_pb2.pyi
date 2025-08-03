import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GuildMemberParametersChangeRequest(_message.Message):
    __slots__ = ("member_id", "rank_id", "experience_given_percent")
    MEMBER_ID_FIELD_NUMBER: _ClassVar[int]
    RANK_ID_FIELD_NUMBER: _ClassVar[int]
    EXPERIENCE_GIVEN_PERCENT_FIELD_NUMBER: _ClassVar[int]
    member_id: int
    rank_id: int
    experience_given_percent: int
    def __init__(self, member_id: _Optional[int] = ..., rank_id: _Optional[int] = ..., experience_given_percent: _Optional[int] = ...) -> None: ...

class GuildMemberWarnOnConnectionStartRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GuildMemberWarnOnConnectionStopRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GuildMemberWarnOnConnectionSetRequest(_message.Message):
    __slots__ = ("enable", "guild_id")
    ENABLE_FIELD_NUMBER: _ClassVar[int]
    GUILD_ID_FIELD_NUMBER: _ClassVar[int]
    enable: bool
    guild_id: str
    def __init__(self, enable: bool = ..., guild_id: _Optional[str] = ...) -> None: ...

class GuildMemberOnlineStatusEvent(_message.Message):
    __slots__ = ("member_id", "online")
    MEMBER_ID_FIELD_NUMBER: _ClassVar[int]
    ONLINE_FIELD_NUMBER: _ClassVar[int]
    member_id: int
    online: bool
    def __init__(self, member_id: _Optional[int] = ..., online: bool = ...) -> None: ...

class GuildMembersEvent(_message.Message):
    __slots__ = ("members",)
    MEMBERS_FIELD_NUMBER: _ClassVar[int]
    members: _containers.RepeatedCompositeFieldContainer[_common_pb2.Character]
    def __init__(self, members: _Optional[_Iterable[_Union[_common_pb2.Character, _Mapping]]] = ...) -> None: ...

class GuildMemberUpdateEvent(_message.Message):
    __slots__ = ("member",)
    MEMBER_FIELD_NUMBER: _ClassVar[int]
    member: _common_pb2.Character
    def __init__(self, member: _Optional[_Union[_common_pb2.Character, _Mapping]] = ...) -> None: ...

class GuildMemberLeaveEvent(_message.Message):
    __slots__ = ("kicked", "player_id")
    KICKED_FIELD_NUMBER: _ClassVar[int]
    PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
    kicked: bool
    player_id: int
    def __init__(self, kicked: bool = ..., player_id: _Optional[int] = ...) -> None: ...

class GuildLeftEvent(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GuildMembershipEvent(_message.Message):
    __slots__ = ("guild_information", "rank_id", "unknown_ftza", "unknown_ftzd")
    GUILD_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    RANK_ID_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FTZA_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FTZD_FIELD_NUMBER: _ClassVar[int]
    guild_information: _common_pb2.GuildInformation
    rank_id: int
    unknown_ftza: int
    unknown_ftzd: int
    def __init__(self, guild_information: _Optional[_Union[_common_pb2.GuildInformation, _Mapping]] = ..., rank_id: _Optional[int] = ..., unknown_ftza: _Optional[int] = ..., unknown_ftzd: _Optional[int] = ...) -> None: ...

class GuildJoinedEvent(_message.Message):
    __slots__ = ("guild_information", "rank_id")
    GUILD_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    RANK_ID_FIELD_NUMBER: _ClassVar[int]
    guild_information: _common_pb2.GuildInformation
    rank_id: int
    def __init__(self, guild_information: _Optional[_Union[_common_pb2.GuildInformation, _Mapping]] = ..., rank_id: _Optional[int] = ...) -> None: ...

class UnknownJkh(_message.Message):
    __slots__ = ("unknown_fttu", "unknown_fttv")
    class UnknownJkf(_message.Message):
        __slots__ = ("unknown_fttp", "unknown_fttq")
        class UnknownFttqEntry(_message.Message):
            __slots__ = ("key", "value")
            KEY_FIELD_NUMBER: _ClassVar[int]
            VALUE_FIELD_NUMBER: _ClassVar[int]
            key: int
            value: UnknownJkt
            def __init__(self, key: _Optional[int] = ..., value: _Optional[_Union[UnknownJkt, _Mapping]] = ...) -> None: ...
        UNKNOWN_FTTP_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FTTQ_FIELD_NUMBER: _ClassVar[int]
        unknown_fttp: int
        unknown_fttq: _containers.MessageMap[int, UnknownJkt]
        def __init__(self, unknown_fttp: _Optional[int] = ..., unknown_fttq: _Optional[_Mapping[int, UnknownJkt]] = ...) -> None: ...
    UNKNOWN_FTTU_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FTTV_FIELD_NUMBER: _ClassVar[int]
    unknown_fttu: int
    unknown_fttv: UnknownJkh.UnknownJkf
    def __init__(self, unknown_fttu: _Optional[int] = ..., unknown_fttv: _Optional[_Union[UnknownJkh.UnknownJkf, _Mapping]] = ...) -> None: ...

class UnknownJkt(_message.Message):
    __slots__ = ("unknown_ftve", "unknown_ftvf")
    UNKNOWN_FTVE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FTVF_FIELD_NUMBER: _ClassVar[int]
    unknown_ftve: int
    unknown_ftvf: UnknownJkq
    def __init__(self, unknown_ftve: _Optional[int] = ..., unknown_ftvf: _Optional[_Union[UnknownJkq, _Mapping]] = ...) -> None: ...

class UnknownJkq(_message.Message):
    __slots__ = ("unknown_ftuq", "unknown_ftur")
    class UnknownJko(_message.Message):
        __slots__ = ("unknown_ftuk", "unknown_ftul")
        UNKNOWN_FTUK_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FTUL_FIELD_NUMBER: _ClassVar[int]
        unknown_ftuk: int
        unknown_ftul: str
        def __init__(self, unknown_ftuk: _Optional[int] = ..., unknown_ftul: _Optional[str] = ...) -> None: ...
    UNKNOWN_FTUQ_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FTUR_FIELD_NUMBER: _ClassVar[int]
    unknown_ftuq: UnknownJkq.UnknownJko
    unknown_ftur: int
    def __init__(self, unknown_ftuq: _Optional[_Union[UnknownJkq.UnknownJko, _Mapping]] = ..., unknown_ftur: _Optional[int] = ...) -> None: ...

class UnknownJku(_message.Message):
    __slots__ = ("unknown_ftvk", "unknown_ftvl")
    class UnknownFtvkEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: int
        def __init__(self, key: _Optional[int] = ..., value: _Optional[int] = ...) -> None: ...
    UNKNOWN_FTVK_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FTVL_FIELD_NUMBER: _ClassVar[int]
    unknown_ftvk: _containers.ScalarMap[int, int]
    unknown_ftvl: int
    def __init__(self, unknown_ftvk: _Optional[_Mapping[int, int]] = ..., unknown_ftvl: _Optional[int] = ...) -> None: ...

class UnknownJkv(_message.Message):
    __slots__ = ("unknown_ftvp", "unknown_ftvq")
    UNKNOWN_FTVP_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FTVQ_FIELD_NUMBER: _ClassVar[int]
    unknown_ftvp: UnknownJkq
    unknown_ftvq: int
    def __init__(self, unknown_ftvp: _Optional[_Union[UnknownJkq, _Mapping]] = ..., unknown_ftvq: _Optional[int] = ...) -> None: ...

class UnknownJkw(_message.Message):
    __slots__ = ("unknown_ftvu",)
    UNKNOWN_FTVU_FIELD_NUMBER: _ClassVar[int]
    unknown_ftvu: int
    def __init__(self, unknown_ftvu: _Optional[int] = ...) -> None: ...

class UnknownJky(_message.Message):
    __slots__ = ("unknown_ftwc",)
    UNKNOWN_FTWC_FIELD_NUMBER: _ClassVar[int]
    unknown_ftwc: int
    def __init__(self, unknown_ftwc: _Optional[int] = ...) -> None: ...
