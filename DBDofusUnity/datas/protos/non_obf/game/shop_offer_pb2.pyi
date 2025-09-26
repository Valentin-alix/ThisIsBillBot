from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class UnknownFourHundredNinetyOne(_message.Message):
    __slots__ = ()
    class UnknownFourHundredNinetyTwo(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN_FOUR_HUNDRED_NINETY_TWO_UNSPECIFIED: _ClassVar[UnknownFourHundredNinetyOne.UnknownFourHundredNinetyTwo]
        UNKNOWN_FOUR_HUNDRED_NINETY_TWO_1: _ClassVar[UnknownFourHundredNinetyOne.UnknownFourHundredNinetyTwo]
    UNKNOWN_FOUR_HUNDRED_NINETY_TWO_UNSPECIFIED: UnknownFourHundredNinetyOne.UnknownFourHundredNinetyTwo
    UNKNOWN_FOUR_HUNDRED_NINETY_TWO_1: UnknownFourHundredNinetyOne.UnknownFourHundredNinetyTwo
    class UnknownFourHundredNinetyThree(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    def __init__(self) -> None: ...

class UnknownFourHundredNinetyFour(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class UnknownFourHundredNinetyFive(_message.Message):
    __slots__ = ("unknown_eight_hundred_fifty_four",)
    UNKNOWN_EIGHT_HUNDRED_FIFTY_FOUR_FIELD_NUMBER: _ClassVar[int]
    unknown_eight_hundred_fifty_four: _containers.RepeatedCompositeFieldContainer[UnknownFourHundredNinetyOne]
    def __init__(self, unknown_eight_hundred_fifty_four: _Optional[_Iterable[_Union[UnknownFourHundredNinetyOne, _Mapping]]] = ...) -> None: ...
