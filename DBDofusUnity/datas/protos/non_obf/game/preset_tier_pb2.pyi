from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TierAmount(_message.Message):
    __slots__ = ("amount", "tier")
    class UnknownFourHundredEightyFour(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN_FOUR_HUNDRED_EIGHTY_FOUR_UNSPECIFIED: _ClassVar[TierAmount.UnknownFourHundredEightyFour]
    UNKNOWN_FOUR_HUNDRED_EIGHTY_FOUR_UNSPECIFIED: TierAmount.UnknownFourHundredEightyFour
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    TIER_FIELD_NUMBER: _ClassVar[int]
    amount: int
    tier: TierAmount.UnknownFourHundredEightyFour
    def __init__(self, amount: _Optional[int] = ..., tier: _Optional[_Union[TierAmount.UnknownFourHundredEightyFour, str]] = ...) -> None: ...

class TierAmountTableEvent(_message.Message):
    __slots__ = ("entries",)
    ENTRIES_FIELD_NUMBER: _ClassVar[int]
    entries: _containers.RepeatedCompositeFieldContainer[TierAmount]
    def __init__(self, entries: _Optional[_Iterable[_Union[TierAmount, _Mapping]]] = ...) -> None: ...
