import ladder_pb2 as _ladder_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ExperienceLadderPageRequest(_message.Message):
    __slots__ = ("unknown_six_hundred_seventy_six", "server_id")
    UNKNOWN_SIX_HUNDRED_SEVENTY_SIX_FIELD_NUMBER: _ClassVar[int]
    SERVER_ID_FIELD_NUMBER: _ClassVar[int]
    unknown_six_hundred_seventy_six: _containers.RepeatedScalarFieldContainer[bool]
    server_id: int
    def __init__(self, unknown_six_hundred_seventy_six: _Optional[_Iterable[bool]] = ..., server_id: _Optional[int] = ...) -> None: ...

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

class UnknownThreeHundredSixtySeven(_message.Message):
    __slots__ = ("unknown_six_hundred_seventy_seven", "unknown_six_hundred_seventy_eight")
    UNKNOWN_SIX_HUNDRED_SEVENTY_SEVEN_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_SIX_HUNDRED_SEVENTY_EIGHT_FIELD_NUMBER: _ClassVar[int]
    unknown_six_hundred_seventy_seven: str
    unknown_six_hundred_seventy_eight: int
    def __init__(self, unknown_six_hundred_seventy_seven: _Optional[str] = ..., unknown_six_hundred_seventy_eight: _Optional[int] = ...) -> None: ...

class UnknownThreeHundredSixtyEight(_message.Message):
    __slots__ = ("entries",)
    ENTRIES_FIELD_NUMBER: _ClassVar[int]
    entries: _containers.RepeatedCompositeFieldContainer[ExperienceLadderEntry]
    def __init__(self, entries: _Optional[_Iterable[_Union[ExperienceLadderEntry, _Mapping]]] = ...) -> None: ...

class ExperienceLadderSelfRankEvent(_message.Message):
    __slots__ = ("entry",)
    ENTRY_FIELD_NUMBER: _ClassVar[int]
    entry: ExperienceLadderEntry
    def __init__(self, entry: _Optional[_Union[ExperienceLadderEntry, _Mapping]] = ...) -> None: ...
