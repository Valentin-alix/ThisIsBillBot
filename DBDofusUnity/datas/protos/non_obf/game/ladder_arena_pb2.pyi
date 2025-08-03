import arena_pb2 as _arena_pb2
import game_message_pb2 as _game_message_pb2
import report_pb2 as _report_pb2
import ladder_pb2 as _ladder_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ArenaLadderPageEvent(_message.Message):
    __slots__ = ("ranks",)
    RANKS_FIELD_NUMBER: _ClassVar[int]
    ranks: _containers.RepeatedCompositeFieldContainer[ArenaLadderEntry]
    def __init__(self, ranks: _Optional[_Iterable[_Union[ArenaLadderEntry, _Mapping]]] = ...) -> None: ...

class ArenaLadderEntry(_message.Message):
    __slots__ = ("rank", "winrate", "player", "unknown_fque", "rating")
    RANK_FIELD_NUMBER: _ClassVar[int]
    WINRATE_FIELD_NUMBER: _ClassVar[int]
    PLAYER_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FQUE_FIELD_NUMBER: _ClassVar[int]
    RATING_FIELD_NUMBER: _ClassVar[int]
    rank: int
    winrate: int
    player: _ladder_pb2.LadderCharacter
    unknown_fque: int
    rating: int
    def __init__(self, rank: _Optional[int] = ..., winrate: _Optional[int] = ..., player: _Optional[_Union[_ladder_pb2.LadderCharacter, _Mapping]] = ..., unknown_fque: _Optional[int] = ..., rating: _Optional[int] = ...) -> None: ...

class ArenaLadderSelfRankRequest(_message.Message):
    __slots__ = ("breed_id", "mode", "unknown_fqto")
    BREED_ID_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FQTO_FIELD_NUMBER: _ClassVar[int]
    breed_id: int
    mode: _arena_pb2.ArenaType
    unknown_fqto: int
    def __init__(self, breed_id: _Optional[int] = ..., mode: _Optional[_Union[_arena_pb2.ArenaType, str]] = ..., unknown_fqto: _Optional[int] = ...) -> None: ...

class UnknownIqv(_message.Message):
    __slots__ = ("entries",)
    ENTRIES_FIELD_NUMBER: _ClassVar[int]
    entries: _containers.RepeatedCompositeFieldContainer[ArenaLadderEntry]
    def __init__(self, entries: _Optional[_Iterable[_Union[ArenaLadderEntry, _Mapping]]] = ...) -> None: ...

class ArenaLadderPageRequest(_message.Message):
    __slots__ = ("unknown_fqul", "mode", "level_range", "breed_id")
    UNKNOWN_FQUL_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    LEVEL_RANGE_FIELD_NUMBER: _ClassVar[int]
    BREED_ID_FIELD_NUMBER: _ClassVar[int]
    unknown_fqul: _containers.RepeatedScalarFieldContainer[bool]
    mode: _arena_pb2.ArenaType
    level_range: int
    breed_id: int
    def __init__(self, unknown_fqul: _Optional[_Iterable[bool]] = ..., mode: _Optional[_Union[_arena_pb2.ArenaType, str]] = ..., level_range: _Optional[int] = ..., breed_id: _Optional[int] = ...) -> None: ...

class UnknownIqz(_message.Message):
    __slots__ = ("unknown_fquu", "unknown_fquw", "unknown_fqux", "unknown_fquz")
    UNKNOWN_FQUU_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FQUW_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FQUX_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FQUZ_FIELD_NUMBER: _ClassVar[int]
    unknown_fquu: int
    unknown_fquw: int
    unknown_fqux: int
    unknown_fquz: str
    def __init__(self, unknown_fquu: _Optional[int] = ..., unknown_fquw: _Optional[int] = ..., unknown_fqux: _Optional[int] = ..., unknown_fquz: _Optional[str] = ...) -> None: ...

class ArenaLadderSelfRankEvent(_message.Message):
    __slots__ = ("entry",)
    ENTRY_FIELD_NUMBER: _ClassVar[int]
    entry: ArenaLadderEntry
    def __init__(self, entry: _Optional[_Union[ArenaLadderEntry, _Mapping]] = ...) -> None: ...
