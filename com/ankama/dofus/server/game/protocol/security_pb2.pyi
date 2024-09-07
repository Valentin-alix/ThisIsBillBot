from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CheckType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    LENGTH: _ClassVar[CheckType]
    HASH_SUM: _ClassVar[CheckType]
LENGTH: CheckType
HASH_SUM: CheckType

class FileCheckRequest(_message.Message):
    __slots__ = ("check_type", "value")
    CHECK_TYPE_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    check_type: CheckType
    value: str
    def __init__(self, check_type: _Optional[_Union[CheckType, str]] = ..., value: _Optional[str] = ...) -> None: ...

class TrustStatusEvent(_message.Message):
    __slots__ = ("certified",)
    CERTIFIED_FIELD_NUMBER: _ClassVar[int]
    certified: bool
    def __init__(self, certified: bool = ...) -> None: ...

class FileCheckEvent(_message.Message):
    __slots__ = ("file_name", "check_type")
    FILE_NAME_FIELD_NUMBER: _ClassVar[int]
    CHECK_TYPE_FIELD_NUMBER: _ClassVar[int]
    file_name: str
    check_type: CheckType
    def __init__(self, file_name: _Optional[str] = ..., check_type: _Optional[_Union[CheckType, str]] = ...) -> None: ...
