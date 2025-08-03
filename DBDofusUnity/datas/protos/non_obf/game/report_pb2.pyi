from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ReportRequest(_message.Message):
    __slots__ = ("report", "unknown_fnvt")
    class ReportCategory(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        THIRD_PARTY_SOFTWARE: _ClassVar[ReportRequest.ReportCategory]
        ILLEGAL_TRADE: _ClassVar[ReportRequest.ReportCategory]
        ILLEGAL_PROMOTION: _ClassVar[ReportRequest.ReportCategory]
        EXPLOITING: _ClassVar[ReportRequest.ReportCategory]
        OFFENSIVE_NAME: _ClassVar[ReportRequest.ReportCategory]
        OFFENSIVE_LANGUAGE: _ClassVar[ReportRequest.ReportCategory]
        PHISHING: _ClassVar[ReportRequest.ReportCategory]
    THIRD_PARTY_SOFTWARE: ReportRequest.ReportCategory
    ILLEGAL_TRADE: ReportRequest.ReportCategory
    ILLEGAL_PROMOTION: ReportRequest.ReportCategory
    EXPLOITING: ReportRequest.ReportCategory
    OFFENSIVE_NAME: ReportRequest.ReportCategory
    OFFENSIVE_LANGUAGE: ReportRequest.ReportCategory
    PHISHING: ReportRequest.ReportCategory
    class Report(_message.Message):
        __slots__ = ("report_category", "description", "target_character_id")
        REPORT_CATEGORY_FIELD_NUMBER: _ClassVar[int]
        DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
        TARGET_CHARACTER_ID_FIELD_NUMBER: _ClassVar[int]
        report_category: ReportRequest.ReportCategory
        description: str
        target_character_id: int
        def __init__(self, report_category: _Optional[_Union[ReportRequest.ReportCategory, str]] = ..., description: _Optional[str] = ..., target_character_id: _Optional[int] = ...) -> None: ...
    class UnknownHvi(_message.Message):
        __slots__ = ("unknown_fnvn", "unknown_fnvo")
        UNKNOWN_FNVN_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FNVO_FIELD_NUMBER: _ClassVar[int]
        unknown_fnvn: str
        unknown_fnvo: str
        def __init__(self, unknown_fnvn: _Optional[str] = ..., unknown_fnvo: _Optional[str] = ...) -> None: ...
    REPORT_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FNVT_FIELD_NUMBER: _ClassVar[int]
    report: ReportRequest.Report
    unknown_fnvt: ReportRequest.UnknownHvi
    def __init__(self, report: _Optional[_Union[ReportRequest.Report, _Mapping]] = ..., unknown_fnvt: _Optional[_Union[ReportRequest.UnknownHvi, _Mapping]] = ...) -> None: ...

class ReportResponse(_message.Message):
    __slots__ = ("reportability_by_character_id", "error", "success")
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
    class ReportabilityByCharacterIdEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: bool
        def __init__(self, key: _Optional[int] = ..., value: bool = ...) -> None: ...
    REPORTABILITY_BY_CHARACTER_ID_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    reportability_by_character_id: _containers.ScalarMap[int, bool]
    error: ReportResponse.Error
    success: bool
    def __init__(self, reportability_by_character_id: _Optional[_Mapping[int, bool]] = ..., error: _Optional[_Union[ReportResponse.Error, str]] = ..., success: bool = ...) -> None: ...
