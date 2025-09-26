import arena_pb2 as _arena_pb2
import ladder_pb2 as _ladder_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class UnknownThreeHundredSixtyTwo(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN_THREE_HUNDRED_SIXTY_TWO: _ClassVar[UnknownThreeHundredSixtyTwo]
UNKNOWN_THREE_HUNDRED_SIXTY_TWO: UnknownThreeHundredSixtyTwo

class ArenaLadderPageEvent(_message.Message):
    __slots__ = ("ranks",)
    RANKS_FIELD_NUMBER: _ClassVar[int]
    ranks: _containers.RepeatedCompositeFieldContainer[ArenaLadderEntry]
    def __init__(self, ranks: _Optional[_Iterable[_Union[ArenaLadderEntry, _Mapping]]] = ...) -> None: ...

class ArenaLadderEntry(_message.Message):
    __slots__ = ("rank", "winrate", "player", "unknown_six_hundred_sixty_six", "rating")
    RANK_FIELD_NUMBER: _ClassVar[int]
    WINRATE_FIELD_NUMBER: _ClassVar[int]
    PLAYER_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_SIX_HUNDRED_SIXTY_SIX_FIELD_NUMBER: _ClassVar[int]
    RATING_FIELD_NUMBER: _ClassVar[int]
    rank: int
    winrate: int
    player: _ladder_pb2.LadderCharacter
    unknown_six_hundred_sixty_six: int
    rating: int
    def __init__(self, rank: _Optional[int] = ..., winrate: _Optional[int] = ..., player: _Optional[_Union[_ladder_pb2.LadderCharacter, _Mapping]] = ..., unknown_six_hundred_sixty_six: _Optional[int] = ..., rating: _Optional[int] = ...) -> None: ...

class ArenaLadderSelfRankRequest(_message.Message):
    __slots__ = ("breed_id", "mode", "unknown_six_hundred_sixty_eight")
    BREED_ID_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_SIX_HUNDRED_SIXTY_EIGHT_FIELD_NUMBER: _ClassVar[int]
    breed_id: int
    mode: _arena_pb2.ArenaType
    unknown_six_hundred_sixty_eight: int
    def __init__(self, breed_id: _Optional[int] = ..., mode: _Optional[_Union[_arena_pb2.ArenaType, str]] = ..., unknown_six_hundred_sixty_eight: _Optional[int] = ...) -> None: ...

class UnknownThreeHundredSixtyThree(_message.Message):
    __slots__ = ("entries",)
    ENTRIES_FIELD_NUMBER: _ClassVar[int]
    entries: _containers.RepeatedCompositeFieldContainer[ArenaLadderEntry]
    def __init__(self, entries: _Optional[_Iterable[_Union[ArenaLadderEntry, _Mapping]]] = ...) -> None: ...

class ArenaLadderPageRequest(_message.Message):
    __slots__ = ("unknown_six_hundred_sixty_seven", "mode", "level_range", "breed_id")
    UNKNOWN_SIX_HUNDRED_SIXTY_SEVEN_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    LEVEL_RANGE_FIELD_NUMBER: _ClassVar[int]
    BREED_ID_FIELD_NUMBER: _ClassVar[int]
    unknown_six_hundred_sixty_seven: _containers.RepeatedScalarFieldContainer[bool]
    mode: _arena_pb2.ArenaType
    level_range: int
    breed_id: int
    def __init__(self, unknown_six_hundred_sixty_seven: _Optional[_Iterable[bool]] = ..., mode: _Optional[_Union[_arena_pb2.ArenaType, str]] = ..., level_range: _Optional[int] = ..., breed_id: _Optional[int] = ...) -> None: ...

class UnknownThreeHundredSixtyFour(_message.Message):
    __slots__ = ("unknown_six_hundred_sixty_nine", "unknown_six_hundred_seventy", "unknown_six_hundred_seventy_one", "unknown_six_hundred_seventy_two")
    UNKNOWN_SIX_HUNDRED_SIXTY_NINE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_SIX_HUNDRED_SEVENTY_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_SIX_HUNDRED_SEVENTY_ONE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_SIX_HUNDRED_SEVENTY_TWO_FIELD_NUMBER: _ClassVar[int]
    unknown_six_hundred_sixty_nine: int
    unknown_six_hundred_seventy: UnknownThreeHundredSixtyTwo
    unknown_six_hundred_seventy_one: int
    unknown_six_hundred_seventy_two: str
    def __init__(self, unknown_six_hundred_sixty_nine: _Optional[int] = ..., unknown_six_hundred_seventy: _Optional[_Union[UnknownThreeHundredSixtyTwo, str]] = ..., unknown_six_hundred_seventy_one: _Optional[int] = ..., unknown_six_hundred_seventy_two: _Optional[str] = ...) -> None: ...

class ArenaLadderSelfRankEvent(_message.Message):
    __slots__ = ("entry",)
    ENTRY_FIELD_NUMBER: _ClassVar[int]
    entry: ArenaLadderEntry
    def __init__(self, entry: _Optional[_Union[ArenaLadderEntry, _Mapping]] = ...) -> None: ...
