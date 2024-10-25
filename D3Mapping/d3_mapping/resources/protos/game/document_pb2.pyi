from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class DocumentReadingBeginEvent(_message.Message):
    __slots__ = ("document_id",)
    DOCUMENT_ID_FIELD_NUMBER: _ClassVar[int]
    document_id: int
    def __init__(self, document_id: _Optional[int] = ...) -> None: ...

class OpenGuideBookEvent(_message.Message):
    __slots__ = ("article_id",)
    ARTICLE_ID_FIELD_NUMBER: _ClassVar[int]
    article_id: int
    def __init__(self, article_id: _Optional[int] = ...) -> None: ...
