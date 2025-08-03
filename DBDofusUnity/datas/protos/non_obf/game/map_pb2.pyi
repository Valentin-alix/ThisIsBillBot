from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class UnknownKsc(_message.Message):
    __slots__ = ("unknown_fyxs", "unknown_fyxt")
    UNKNOWN_FYXS_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FYXT_FIELD_NUMBER: _ClassVar[int]
    unknown_fyxs: int
    unknown_fyxt: bool
    def __init__(self, unknown_fyxs: _Optional[int] = ..., unknown_fyxt: bool = ...) -> None: ...
