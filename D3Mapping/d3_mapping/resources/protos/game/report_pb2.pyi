from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ReportRequest(_message.Message):
    __slots__ = ("actor_id", "categories", "description")
    class Category(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        CHEATING: _ClassVar[ReportRequest.Category]
        ILLEGAL_TRADE: _ClassVar[ReportRequest.Category]
        ILLEGAL_PROMOTE: _ClassVar[ReportRequest.Category]
        EXPLOITING: _ClassVar[ReportRequest.Category]
        OFFENSIVE_NAME: _ClassVar[ReportRequest.Category]
        VERBAL_ABUSE: _ClassVar[ReportRequest.Category]
        PHISHING: _ClassVar[ReportRequest.Category]
    CHEATING: ReportRequest.Category
    ILLEGAL_TRADE: ReportRequest.Category
    ILLEGAL_PROMOTE: ReportRequest.Category
    EXPLOITING: ReportRequest.Category
    OFFENSIVE_NAME: ReportRequest.Category
    VERBAL_ABUSE: ReportRequest.Category
    PHISHING: ReportRequest.Category
    ACTOR_ID_FIELD_NUMBER: _ClassVar[int]
    CATEGORIES_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    actor_id: int
    categories: ReportRequest.Category
    description: str
    def __init__(self, actor_id: _Optional[int] = ..., categories: _Optional[_Union[ReportRequest.Category, str]] = ..., description: _Optional[str] = ...) -> None: ...

class ReportResponse(_message.Message):
    __slots__ = ("success", "error")
    class Error(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN: _ClassVar[ReportResponse.Error]
        SUBSCRIPTION_REQUIRED: _ClassVar[ReportResponse.Error]
        BAD_LEVEL: _ClassVar[ReportResponse.Error]
        LIMIT_EXCEEDED: _ClassVar[ReportResponse.Error]
        NOT_ENABLED: _ClassVar[ReportResponse.Error]
        ALREADY_REPORTED: _ClassVar[ReportResponse.Error]
    UNKNOWN: ReportResponse.Error
    SUBSCRIPTION_REQUIRED: ReportResponse.Error
    BAD_LEVEL: ReportResponse.Error
    LIMIT_EXCEEDED: ReportResponse.Error
    NOT_ENABLED: ReportResponse.Error
    ALREADY_REPORTED: ReportResponse.Error
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: bool
    error: ReportResponse.Error
    def __init__(self, success: bool = ..., error: _Optional[_Union[ReportResponse.Error, str]] = ...) -> None: ...
