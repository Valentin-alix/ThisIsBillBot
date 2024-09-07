from google.protobuf import any_pb2 as _any_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Message(_message.Message):
    __slots__ = ("request", "response", "event")
    REQUEST_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    EVENT_FIELD_NUMBER: _ClassVar[int]
    request: Request
    response: Response
    event: Event
    def __init__(self, request: _Optional[_Union[Request, _Mapping]] = ..., response: _Optional[_Union[Response, _Mapping]] = ..., event: _Optional[_Union[Event, _Mapping]] = ...) -> None: ...

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
