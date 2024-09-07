from com.ankama.dofus.server.game.protocol import common_pb2 as _common_pb2
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
    __slots__ = ("guild_information", "rank_id")
    GUILD_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    RANK_ID_FIELD_NUMBER: _ClassVar[int]
    guild_information: _common_pb2.GuildInformation
    rank_id: int
    def __init__(self, guild_information: _Optional[_Union[_common_pb2.GuildInformation, _Mapping]] = ..., rank_id: _Optional[int] = ...) -> None: ...

class GuildJoinedEvent(_message.Message):
    __slots__ = ("guild_information", "rank_id")
    GUILD_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    RANK_ID_FIELD_NUMBER: _ClassVar[int]
    guild_information: _common_pb2.GuildInformation
    rank_id: int
    def __init__(self, guild_information: _Optional[_Union[_common_pb2.GuildInformation, _Mapping]] = ..., rank_id: _Optional[int] = ...) -> None: ...
