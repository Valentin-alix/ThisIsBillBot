import common_pb2 as _common_pb2
import game_message_pb2 as _game_message_pb2
import report_pb2 as _report_pb2
import ladder_pb2 as _ladder_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class InfiniteDreamLadderPageEvent(_message.Message):
    __slots__ = ("entries",)
    ENTRIES_FIELD_NUMBER: _ClassVar[int]
    entries: _containers.RepeatedCompositeFieldContainer[InfiniteDreamLadderEntry]
    def __init__(self, entries: _Optional[_Iterable[_Union[InfiniteDreamLadderEntry, _Mapping]]] = ...) -> None: ...

class UnknownIqk(_message.Message):
    __slots__ = ("unknown_fqrv", "unknown_fqrw")
    UNKNOWN_FQRV_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FQRW_FIELD_NUMBER: _ClassVar[int]
    unknown_fqrv: int
    unknown_fqrw: str
    def __init__(self, unknown_fqrv: _Optional[int] = ..., unknown_fqrw: _Optional[str] = ...) -> None: ...

class InfiniteDreamLadderSelfRankRequest(_message.Message):
    __slots__ = ("server_id",)
    SERVER_ID_FIELD_NUMBER: _ClassVar[int]
    server_id: int
    def __init__(self, server_id: _Optional[int] = ...) -> None: ...

class UnknownIqm(_message.Message):
    __slots__ = ("entries",)
    ENTRIES_FIELD_NUMBER: _ClassVar[int]
    entries: _containers.RepeatedCompositeFieldContainer[InfiniteDreamLadderEntry]
    def __init__(self, entries: _Optional[_Iterable[_Union[InfiniteDreamLadderEntry, _Mapping]]] = ...) -> None: ...

class InfiniteDreamLadderPageRequest(_message.Message):
    __slots__ = ("server_id",)
    SERVER_ID_FIELD_NUMBER: _ClassVar[int]
    server_id: int
    def __init__(self, server_id: _Optional[int] = ...) -> None: ...

class InfiniteDreamLadderSelfRankEvent(_message.Message):
    __slots__ = ("entry",)
    ENTRY_FIELD_NUMBER: _ClassVar[int]
    entry: InfiniteDreamLadderEntry
    def __init__(self, entry: _Optional[_Union[InfiniteDreamLadderEntry, _Mapping]] = ...) -> None: ...

class InfiniteDreamLadderEntry(_message.Message):
    __slots__ = ("unknown_fqsj", "rank", "player", "breed_id", "done_date", "wave")
    UNKNOWN_FQSJ_FIELD_NUMBER: _ClassVar[int]
    RANK_FIELD_NUMBER: _ClassVar[int]
    PLAYER_FIELD_NUMBER: _ClassVar[int]
    BREED_ID_FIELD_NUMBER: _ClassVar[int]
    DONE_DATE_FIELD_NUMBER: _ClassVar[int]
    WAVE_FIELD_NUMBER: _ClassVar[int]
    unknown_fqsj: int
    rank: int
    player: _ladder_pb2.LadderCharacter
    breed_id: int
    done_date: str
    wave: int
    def __init__(self, unknown_fqsj: _Optional[int] = ..., rank: _Optional[int] = ..., player: _Optional[_Union[_ladder_pb2.LadderCharacter, _Mapping]] = ..., breed_id: _Optional[int] = ..., done_date: _Optional[str] = ..., wave: _Optional[int] = ...) -> None: ...
