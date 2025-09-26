import ladder_pb2 as _ladder_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class BreachLadderPageEvent(_message.Message):
    __slots__ = ("entries",)
    ENTRIES_FIELD_NUMBER: _ClassVar[int]
    entries: _containers.RepeatedCompositeFieldContainer[BreachLadderEntry]
    def __init__(self, entries: _Optional[_Iterable[_Union[BreachLadderEntry, _Mapping]]] = ...) -> None: ...

class UnknownThreeHundredSixtyFive(_message.Message):
    __slots__ = ("unknown_six_hundred_seventy_four", "unknown_six_hundred_seventy_five")
    UNKNOWN_SIX_HUNDRED_SEVENTY_FOUR_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_SIX_HUNDRED_SEVENTY_FIVE_FIELD_NUMBER: _ClassVar[int]
    unknown_six_hundred_seventy_four: int
    unknown_six_hundred_seventy_five: str
    def __init__(self, unknown_six_hundred_seventy_four: _Optional[int] = ..., unknown_six_hundred_seventy_five: _Optional[str] = ...) -> None: ...

class BreachLadderSelfRankRequest(_message.Message):
    __slots__ = ("server_id",)
    SERVER_ID_FIELD_NUMBER: _ClassVar[int]
    server_id: int
    def __init__(self, server_id: _Optional[int] = ...) -> None: ...

class UnknownThreeHundredSixtySix(_message.Message):
    __slots__ = ("entries",)
    ENTRIES_FIELD_NUMBER: _ClassVar[int]
    entries: _containers.RepeatedCompositeFieldContainer[BreachLadderEntry]
    def __init__(self, entries: _Optional[_Iterable[_Union[BreachLadderEntry, _Mapping]]] = ...) -> None: ...

class BreachLadderPageRequest(_message.Message):
    __slots__ = ("server_id",)
    SERVER_ID_FIELD_NUMBER: _ClassVar[int]
    server_id: int
    def __init__(self, server_id: _Optional[int] = ...) -> None: ...

class BreachLadderSelfRankEvent(_message.Message):
    __slots__ = ("entry",)
    ENTRY_FIELD_NUMBER: _ClassVar[int]
    entry: BreachLadderEntry
    def __init__(self, entry: _Optional[_Union[BreachLadderEntry, _Mapping]] = ...) -> None: ...

class BreachLadderEntry(_message.Message):
    __slots__ = ("unknown_six_hundred_seventy_three", "rank", "player", "breed_id", "done_date", "wave")
    UNKNOWN_SIX_HUNDRED_SEVENTY_THREE_FIELD_NUMBER: _ClassVar[int]
    RANK_FIELD_NUMBER: _ClassVar[int]
    PLAYER_FIELD_NUMBER: _ClassVar[int]
    BREED_ID_FIELD_NUMBER: _ClassVar[int]
    DONE_DATE_FIELD_NUMBER: _ClassVar[int]
    WAVE_FIELD_NUMBER: _ClassVar[int]
    unknown_six_hundred_seventy_three: int
    rank: int
    player: _ladder_pb2.LadderCharacter
    breed_id: int
    done_date: str
    wave: int
    def __init__(self, unknown_six_hundred_seventy_three: _Optional[int] = ..., rank: _Optional[int] = ..., player: _Optional[_Union[_ladder_pb2.LadderCharacter, _Mapping]] = ..., breed_id: _Optional[int] = ..., done_date: _Optional[str] = ..., wave: _Optional[int] = ...) -> None: ...
