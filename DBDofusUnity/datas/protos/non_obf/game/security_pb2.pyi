import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

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

class UnknownLvf(_message.Message):
    __slots__ = ("unknown_gdhg", "unknown_gdhh")
    UNKNOWN_GDHG_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_GDHH_FIELD_NUMBER: _ClassVar[int]
    unknown_gdhg: int
    unknown_gdhh: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, unknown_gdhg: _Optional[int] = ..., unknown_gdhh: _Optional[_Iterable[int]] = ...) -> None: ...

class UnknownLvq(_message.Message):
    __slots__ = ("unknown_gdiw", "unknown_gdix", "unknown_gdiy", "unknown_gdiz", "unknown_gdja")
    class UnknownGdizValue(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN_GDIZ_VALUE_UNSPECIFIED: _ClassVar[UnknownLvq.UnknownGdizValue]
    UNKNOWN_GDIZ_VALUE_UNSPECIFIED: UnknownLvq.UnknownGdizValue
    UNKNOWN_GDIW_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_GDIX_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_GDIY_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_GDIZ_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_GDJA_FIELD_NUMBER: _ClassVar[int]
    unknown_gdiw: int
    unknown_gdix: _containers.RepeatedScalarFieldContainer[int]
    unknown_gdiy: str
    unknown_gdiz: UnknownLvq.UnknownGdizValue
    unknown_gdja: int
    def __init__(self, unknown_gdiw: _Optional[int] = ..., unknown_gdix: _Optional[_Iterable[int]] = ..., unknown_gdiy: _Optional[str] = ..., unknown_gdiz: _Optional[_Union[UnknownLvq.UnknownGdizValue, str]] = ..., unknown_gdja: _Optional[int] = ...) -> None: ...

class UnknownLvv(_message.Message):
    __slots__ = ("unknown_gdjv", "unknown_gdjw", "unknown_gdka")
    class UnknownGdjvValue(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN_GDJV_VALUE_UNSPECIFIED: _ClassVar[UnknownLvv.UnknownGdjvValue]
    UNKNOWN_GDJV_VALUE_UNSPECIFIED: UnknownLvv.UnknownGdjvValue
    UNKNOWN_GDJV_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_GDJW_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_GDKA_FIELD_NUMBER: _ClassVar[int]
    unknown_gdjv: UnknownLvv.UnknownGdjvValue
    unknown_gdjw: _common_pb2.EntityLook
    unknown_gdka: str
    def __init__(self, unknown_gdjv: _Optional[_Union[UnknownLvv.UnknownGdjvValue, str]] = ..., unknown_gdjw: _Optional[_Union[_common_pb2.EntityLook, _Mapping]] = ..., unknown_gdka: _Optional[str] = ...) -> None: ...

class UnknownLwd(_message.Message):
    __slots__ = ("unknown_gdlt", "unknown_gdlu")
    class UnknownGdltValue(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN_GDLT_VALUE_UNSPECIFIED: _ClassVar[UnknownLwd.UnknownGdltValue]
    UNKNOWN_GDLT_VALUE_UNSPECIFIED: UnknownLwd.UnknownGdltValue
    UNKNOWN_GDLT_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_GDLU_FIELD_NUMBER: _ClassVar[int]
    unknown_gdlt: UnknownLwd.UnknownGdltValue
    unknown_gdlu: str
    def __init__(self, unknown_gdlt: _Optional[_Union[UnknownLwd.UnknownGdltValue, str]] = ..., unknown_gdlu: _Optional[str] = ...) -> None: ...

class UnknownLwe(_message.Message):
    __slots__ = ("unknown_gdly", "unknown_gdlz", "unknown_gdma", "unknown_gdmb", "unknown_gdmc", "unknown_gdmd")
    class UnknownGdmaValue(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN_GDMA_VALUE_UNSPECIFIED: _ClassVar[UnknownLwe.UnknownGdmaValue]
    UNKNOWN_GDMA_VALUE_UNSPECIFIED: UnknownLwe.UnknownGdmaValue
    UNKNOWN_GDLY_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_GDLZ_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_GDMA_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_GDMB_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_GDMC_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_GDMD_FIELD_NUMBER: _ClassVar[int]
    unknown_gdly: int
    unknown_gdlz: int
    unknown_gdma: UnknownLwe.UnknownGdmaValue
    unknown_gdmb: int
    unknown_gdmc: str
    unknown_gdmd: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, unknown_gdly: _Optional[int] = ..., unknown_gdlz: _Optional[int] = ..., unknown_gdma: _Optional[_Union[UnknownLwe.UnknownGdmaValue, str]] = ..., unknown_gdmb: _Optional[int] = ..., unknown_gdmc: _Optional[str] = ..., unknown_gdmd: _Optional[_Iterable[int]] = ...) -> None: ...
