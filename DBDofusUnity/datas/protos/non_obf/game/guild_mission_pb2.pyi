from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class UnknownJlb(_message.Message):
    __slots__ = ("unknown_ftwm", "unknown_ftwn")
    UNKNOWN_FTWM_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FTWN_FIELD_NUMBER: _ClassVar[int]
    unknown_ftwm: int
    unknown_ftwn: str
    def __init__(self, unknown_ftwm: _Optional[int] = ..., unknown_ftwn: _Optional[str] = ...) -> None: ...
