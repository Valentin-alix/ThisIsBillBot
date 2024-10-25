from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class CinematicEvent(_message.Message):
    __slots__ = ("cinematic_id",)
    CINEMATIC_ID_FIELD_NUMBER: _ClassVar[int]
    cinematic_id: int
    def __init__(self, cinematic_id: _Optional[int] = ...) -> None: ...
