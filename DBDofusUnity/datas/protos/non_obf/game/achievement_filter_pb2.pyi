from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class AchievementFilterRequest(_message.Message):
    __slots__ = ("filter_text",)
    FILTER_TEXT_FIELD_NUMBER: _ClassVar[int]
    filter_text: str
    def __init__(self, filter_text: _Optional[str] = ...) -> None: ...
