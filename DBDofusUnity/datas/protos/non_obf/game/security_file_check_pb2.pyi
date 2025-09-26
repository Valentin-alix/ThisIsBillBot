from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class UnknownFourHundredEightySeven(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN_FOUR_HUNDRED_EIGHTY_SEVEN_UNSPECIFIED: _ClassVar[UnknownFourHundredEightySeven]
    UNKNOWN_FOUR_HUNDRED_EIGHTY_SEVEN_1: _ClassVar[UnknownFourHundredEightySeven]
UNKNOWN_FOUR_HUNDRED_EIGHTY_SEVEN_UNSPECIFIED: UnknownFourHundredEightySeven
UNKNOWN_FOUR_HUNDRED_EIGHTY_SEVEN_1: UnknownFourHundredEightySeven

class UnknownFourHundredEightyEight(_message.Message):
    __slots__ = ("unknown_eight_hundred_forty_nine", "unknown_eight_hundred_fifty")
    UNKNOWN_EIGHT_HUNDRED_FORTY_NINE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_EIGHT_HUNDRED_FIFTY_FIELD_NUMBER: _ClassVar[int]
    unknown_eight_hundred_forty_nine: UnknownFourHundredEightySeven
    unknown_eight_hundred_fifty: str
    def __init__(self, unknown_eight_hundred_forty_nine: _Optional[_Union[UnknownFourHundredEightySeven, str]] = ..., unknown_eight_hundred_fifty: _Optional[str] = ...) -> None: ...

class UnknownFourHundredEightyNine(_message.Message):
    __slots__ = ("unknown_eight_hundred_fifty_one", "unknown_eight_hundred_fifty_two")
    UNKNOWN_EIGHT_HUNDRED_FIFTY_ONE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_EIGHT_HUNDRED_FIFTY_TWO_FIELD_NUMBER: _ClassVar[int]
    unknown_eight_hundred_fifty_one: str
    unknown_eight_hundred_fifty_two: UnknownFourHundredEightySeven
    def __init__(self, unknown_eight_hundred_fifty_one: _Optional[str] = ..., unknown_eight_hundred_fifty_two: _Optional[_Union[UnknownFourHundredEightySeven, str]] = ...) -> None: ...

class UnknownFourHundredNinety(_message.Message):
    __slots__ = ("unknown_eight_hundred_fifty_three",)
    UNKNOWN_EIGHT_HUNDRED_FIFTY_THREE_FIELD_NUMBER: _ClassVar[int]
    unknown_eight_hundred_fifty_three: bool
    def __init__(self, unknown_eight_hundred_fifty_three: bool = ...) -> None: ...
