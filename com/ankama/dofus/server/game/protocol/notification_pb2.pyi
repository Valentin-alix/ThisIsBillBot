from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class NotificationUpdateFlagRequest(_message.Message):
    __slots__ = ("index",)
    INDEX_FIELD_NUMBER: _ClassVar[int]
    index: int
    def __init__(self, index: _Optional[int] = ...) -> None: ...

class NotificationResetRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class NotificationsEvent(_message.Message):
    __slots__ = ("flags",)
    FLAGS_FIELD_NUMBER: _ClassVar[int]
    flags: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, flags: _Optional[_Iterable[int]] = ...) -> None: ...

class NotificationEvent(_message.Message):
    __slots__ = ("id", "parameters", "force")
    ID_FIELD_NUMBER: _ClassVar[int]
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    FORCE_FIELD_NUMBER: _ClassVar[int]
    id: int
    parameters: _containers.RepeatedScalarFieldContainer[str]
    force: bool
    def __init__(self, id: _Optional[int] = ..., parameters: _Optional[_Iterable[str]] = ..., force: bool = ...) -> None: ...

class RemoveNotificationEvent(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, id: _Optional[_Iterable[int]] = ...) -> None: ...
