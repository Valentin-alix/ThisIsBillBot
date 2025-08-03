from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class PopupWarningCloseRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class PopupWarningEvent(_message.Message):
    __slots__ = ("lock_duration", "author", "content")
    LOCK_DURATION_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    lock_duration: int
    author: str
    content: str
    def __init__(self, lock_duration: _Optional[int] = ..., author: _Optional[str] = ..., content: _Optional[str] = ...) -> None: ...

class PopupWarningClosedEvent(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
