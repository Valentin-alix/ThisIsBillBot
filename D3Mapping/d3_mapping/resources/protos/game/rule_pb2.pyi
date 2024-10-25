import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class NameCompliance(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    NAME_OK: _ClassVar[NameCompliance]
    NAME_ERROR_SERVICE_UNAVAILABLE: _ClassVar[NameCompliance]
    NAME_ERROR_ALREADY_EXISTS: _ClassVar[NameCompliance]
    NAME_ERROR_BAD_ALPHABET: _ClassVar[NameCompliance]
    NAME_ERROR_BAD_LENGTH: _ClassVar[NameCompliance]
    NAME_ERROR_BAD_CHAR: _ClassVar[NameCompliance]
    NAME_ERROR_INVALID_DASH_POSITION: _ClassVar[NameCompliance]
    NAME_ERROR_NAME_WITH_BAD_CASE: _ClassVar[NameCompliance]
    NAME_ERROR_TOO_MANY_CONSECUTIVE_IDENTICAL: _ClassVar[NameCompliance]
    NAME_ERROR_TOO_MANY_SPECIAL: _ClassVar[NameCompliance]
    NAME_ERROR_FORBIDDEN: _ClassVar[NameCompliance]
    NAME_ERROR_RESERVED: _ClassVar[NameCompliance]
NAME_OK: NameCompliance
NAME_ERROR_SERVICE_UNAVAILABLE: NameCompliance
NAME_ERROR_ALREADY_EXISTS: NameCompliance
NAME_ERROR_BAD_ALPHABET: NameCompliance
NAME_ERROR_BAD_LENGTH: NameCompliance
NAME_ERROR_BAD_CHAR: NameCompliance
NAME_ERROR_INVALID_DASH_POSITION: NameCompliance
NAME_ERROR_NAME_WITH_BAD_CASE: NameCompliance
NAME_ERROR_TOO_MANY_CONSECUTIVE_IDENTICAL: NameCompliance
NAME_ERROR_TOO_MANY_SPECIAL: NameCompliance
NAME_ERROR_FORBIDDEN: NameCompliance
NAME_ERROR_RESERVED: NameCompliance

class CharacterUpdateBreedRequest(_message.Message):
    __slots__ = ("breed_id", "gender", "colors", "cosmetic_id", "object_id")
    BREED_ID_FIELD_NUMBER: _ClassVar[int]
    GENDER_FIELD_NUMBER: _ClassVar[int]
    COLORS_FIELD_NUMBER: _ClassVar[int]
    COSMETIC_ID_FIELD_NUMBER: _ClassVar[int]
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    breed_id: int
    gender: _common_pb2.Gender
    colors: _containers.RepeatedScalarFieldContainer[int]
    cosmetic_id: int
    object_id: str
    def __init__(self, breed_id: _Optional[int] = ..., gender: _Optional[_Union[_common_pb2.Gender, str]] = ..., colors: _Optional[_Iterable[int]] = ..., cosmetic_id: _Optional[int] = ..., object_id: _Optional[str] = ...) -> None: ...
