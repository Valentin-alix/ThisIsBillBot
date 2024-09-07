from com.ankama.dofus.server.game.protocol import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GuildRanksRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GuildRankCreateRequest(_message.Message):
    __slots__ = ("parent_rank_id", "gfx_id", "name")
    PARENT_RANK_ID_FIELD_NUMBER: _ClassVar[int]
    GFX_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    parent_rank_id: int
    gfx_id: int
    name: str
    def __init__(self, parent_rank_id: _Optional[int] = ..., gfx_id: _Optional[int] = ..., name: _Optional[str] = ...) -> None: ...

class GuildRankUpdateAllRequest(_message.Message):
    __slots__ = ("ranks",)
    RANKS_FIELD_NUMBER: _ClassVar[int]
    ranks: _containers.RepeatedCompositeFieldContainer[_common_pb2.RankInformation]
    def __init__(self, ranks: _Optional[_Iterable[_Union[_common_pb2.RankInformation, _Mapping]]] = ...) -> None: ...

class GuildRankUpdateRequest(_message.Message):
    __slots__ = ("rank",)
    RANK_FIELD_NUMBER: _ClassVar[int]
    rank: _common_pb2.RankInformation
    def __init__(self, rank: _Optional[_Union[_common_pb2.RankInformation, _Mapping]] = ...) -> None: ...

class GuildRightsUpdateRequest(_message.Message):
    __slots__ = ("rank_id", "rights")
    RANK_ID_FIELD_NUMBER: _ClassVar[int]
    RIGHTS_FIELD_NUMBER: _ClassVar[int]
    rank_id: int
    rights: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, rank_id: _Optional[int] = ..., rights: _Optional[_Iterable[int]] = ...) -> None: ...

class GuildRankRemoveRequest(_message.Message):
    __slots__ = ("rank_id", "new_rank_id")
    RANK_ID_FIELD_NUMBER: _ClassVar[int]
    NEW_RANK_ID_FIELD_NUMBER: _ClassVar[int]
    rank_id: int
    new_rank_id: int
    def __init__(self, rank_id: _Optional[int] = ..., new_rank_id: _Optional[int] = ...) -> None: ...

class GuildRanksEvent(_message.Message):
    __slots__ = ("ranks",)
    RANKS_FIELD_NUMBER: _ClassVar[int]
    ranks: _containers.RepeatedCompositeFieldContainer[_common_pb2.RankInformation]
    def __init__(self, ranks: _Optional[_Iterable[_Union[_common_pb2.RankInformation, _Mapping]]] = ...) -> None: ...
