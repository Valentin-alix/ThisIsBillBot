import ladder_pb2 as _ladder_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class UnknownThreeHundredSixty(_message.Message):
    __slots__ = ("unknown_six_hundred_sixty_four", "unknown_six_hundred_sixty_five")
    UNKNOWN_SIX_HUNDRED_SIXTY_FOUR_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_SIX_HUNDRED_SIXTY_FIVE_FIELD_NUMBER: _ClassVar[int]
    unknown_six_hundred_sixty_four: int
    unknown_six_hundred_sixty_five: str
    def __init__(self, unknown_six_hundred_sixty_four: _Optional[int] = ..., unknown_six_hundred_sixty_five: _Optional[str] = ...) -> None: ...

class AchievementLadderPageEvent(_message.Message):
    __slots__ = ("entries",)
    ENTRIES_FIELD_NUMBER: _ClassVar[int]
    entries: _containers.RepeatedCompositeFieldContainer[AchievementLadderEntry]
    def __init__(self, entries: _Optional[_Iterable[_Union[AchievementLadderEntry, _Mapping]]] = ...) -> None: ...

class AchievementLadderEntry(_message.Message):
    __slots__ = ("rank", "success", "info")
    RANK_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    INFO_FIELD_NUMBER: _ClassVar[int]
    rank: int
    success: int
    info: _ladder_pb2.LadderCharacter
    def __init__(self, rank: _Optional[int] = ..., success: _Optional[int] = ..., info: _Optional[_Union[_ladder_pb2.LadderCharacter, _Mapping]] = ...) -> None: ...

class AchievementLadderPageRequest(_message.Message):
    __slots__ = ("server_id",)
    SERVER_ID_FIELD_NUMBER: _ClassVar[int]
    server_id: int
    def __init__(self, server_id: _Optional[int] = ...) -> None: ...

class UnknownThreeHundredSixtyOne(_message.Message):
    __slots__ = ("entries",)
    ENTRIES_FIELD_NUMBER: _ClassVar[int]
    entries: _containers.RepeatedCompositeFieldContainer[AchievementLadderEntry]
    def __init__(self, entries: _Optional[_Iterable[_Union[AchievementLadderEntry, _Mapping]]] = ...) -> None: ...

class AchievementLadderSelfRankEvent(_message.Message):
    __slots__ = ("entry",)
    ENTRY_FIELD_NUMBER: _ClassVar[int]
    entry: AchievementLadderEntry
    def __init__(self, entry: _Optional[_Union[AchievementLadderEntry, _Mapping]] = ...) -> None: ...

class AchievementLadderSelfRankRequest(_message.Message):
    __slots__ = ("server_id",)
    SERVER_ID_FIELD_NUMBER: _ClassVar[int]
    server_id: int
    def __init__(self, server_id: _Optional[int] = ...) -> None: ...
