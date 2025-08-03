from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class EmotePlayRequest(_message.Message):
    __slots__ = ("emote_id", "only_play_emote")
    EMOTE_ID_FIELD_NUMBER: _ClassVar[int]
    ONLY_PLAY_EMOTE_FIELD_NUMBER: _ClassVar[int]
    emote_id: int
    only_play_emote: bool
    def __init__(self, emote_id: _Optional[int] = ..., only_play_emote: bool = ...) -> None: ...

class EmotesEvent(_message.Message):
    __slots__ = ("emotes_id",)
    EMOTES_ID_FIELD_NUMBER: _ClassVar[int]
    emotes_id: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, emotes_id: _Optional[_Iterable[int]] = ...) -> None: ...

class EmoteAddedEvent(_message.Message):
    __slots__ = ("emote_id",)
    EMOTE_ID_FIELD_NUMBER: _ClassVar[int]
    emote_id: int
    def __init__(self, emote_id: _Optional[int] = ...) -> None: ...

class EmoteRemovedEvent(_message.Message):
    __slots__ = ("emote_id",)
    EMOTE_ID_FIELD_NUMBER: _ClassVar[int]
    emote_id: int
    def __init__(self, emote_id: _Optional[int] = ...) -> None: ...

class EmotePlayEvent(_message.Message):
    __slots__ = ("emote_id", "emote_start_time", "actor_id", "account_id")
    EMOTE_ID_FIELD_NUMBER: _ClassVar[int]
    EMOTE_START_TIME_FIELD_NUMBER: _ClassVar[int]
    ACTOR_ID_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    emote_id: int
    emote_start_time: int
    actor_id: int
    account_id: int
    def __init__(self, emote_id: _Optional[int] = ..., emote_start_time: _Optional[int] = ..., actor_id: _Optional[int] = ..., account_id: _Optional[int] = ...) -> None: ...

class EmoteMassivePlayEvent(_message.Message):
    __slots__ = ("emote_id", "emote_start_time", "actors_id")
    EMOTE_ID_FIELD_NUMBER: _ClassVar[int]
    EMOTE_START_TIME_FIELD_NUMBER: _ClassVar[int]
    ACTORS_ID_FIELD_NUMBER: _ClassVar[int]
    emote_id: int
    emote_start_time: int
    actors_id: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, emote_id: _Optional[int] = ..., emote_start_time: _Optional[int] = ..., actors_id: _Optional[_Iterable[int]] = ...) -> None: ...

class EmotePlayErrorEvent(_message.Message):
    __slots__ = ("emote_id",)
    EMOTE_ID_FIELD_NUMBER: _ClassVar[int]
    emote_id: int
    def __init__(self, emote_id: _Optional[int] = ...) -> None: ...
