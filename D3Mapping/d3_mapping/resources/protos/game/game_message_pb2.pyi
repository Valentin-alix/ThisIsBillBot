from google.protobuf import any_pb2 as _any_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GameMessage(_message.Message):
    __slots__ = ("unknown", "request", "response", "event")
    class Unknown(_message.Message):
        __slots__ = ("unknown_one", "unknown_two", "unknown_three", "unknown_four")
        UNKNOWN_ONE_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_TWO_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_THREE_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FOUR_FIELD_NUMBER: _ClassVar[int]
        unknown_one: int
        unknown_two: str
        unknown_three: int
        unknown_four: int
        def __init__(self, unknown_one: _Optional[int] = ..., unknown_two: _Optional[str] = ..., unknown_three: _Optional[int] = ..., unknown_four: _Optional[int] = ...) -> None: ...
    UNKNOWN_FIELD_NUMBER: _ClassVar[int]
    REQUEST_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    EVENT_FIELD_NUMBER: _ClassVar[int]
    unknown: GameMessage.Unknown
    request: Request
    response: Response
    event: Event
    def __init__(self, unknown: _Optional[_Union[GameMessage.Unknown, _Mapping]] = ..., request: _Optional[_Union[Request, _Mapping]] = ..., response: _Optional[_Union[Response, _Mapping]] = ..., event: _Optional[_Union[Event, _Mapping]] = ...) -> None: ...

class Request(_message.Message):
    __slots__ = ("uid", "content")
    UID_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    uid: int
    content: _any_pb2.Any
    def __init__(self, uid: _Optional[int] = ..., content: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...

class Response(_message.Message):
    __slots__ = ("uid", "content")
    UID_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    uid: int
    content: _any_pb2.Any
    def __init__(self, uid: _Optional[int] = ..., content: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...

class Event(_message.Message):
    __slots__ = ("content",)
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    content: _any_pb2.Any
    def __init__(self, content: _Optional[_Union[_any_pb2.Any, _Mapping]] = ...) -> None: ...
