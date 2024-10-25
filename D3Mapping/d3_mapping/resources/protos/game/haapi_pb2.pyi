from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class HaapiTokenRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class HaapiTokenEvent(_message.Message):
    __slots__ = ("token",)
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    token: str
    def __init__(self, token: _Optional[str] = ...) -> None: ...

class HaapiAuthenticationErrorEvent(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class HaapiSessionEvent(_message.Message):
    __slots__ = ("session_uid",)
    SESSION_UID_FIELD_NUMBER: _ClassVar[int]
    session_uid: str
    def __init__(self, session_uid: _Optional[str] = ...) -> None: ...
