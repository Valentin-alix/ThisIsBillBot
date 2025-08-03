from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class UnknownIpm(_message.Message):
    __slots__ = ("unknown_ejhm",)
    UNKNOWN_EJHM_FIELD_NUMBER: _ClassVar[int]
    unknown_ejhm: int
    def __init__(self, unknown_ejhm: _Optional[int] = ...) -> None: ...
