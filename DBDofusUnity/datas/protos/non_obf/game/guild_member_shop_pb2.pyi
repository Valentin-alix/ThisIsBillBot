from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class UnknownTwoHundredFortySix(_message.Message):
    __slots__ = ()
    class UnknownTwoHundredFortyEight(_message.Message):
        __slots__ = ("unknown_four_hundred_eighty_two", "unknown_four_hundred_eighty_three")
        UNKNOWN_FOUR_HUNDRED_EIGHTY_TWO_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FOUR_HUNDRED_EIGHTY_THREE_FIELD_NUMBER: _ClassVar[int]
        unknown_four_hundred_eighty_two: int
        unknown_four_hundred_eighty_three: str
        def __init__(self, unknown_four_hundred_eighty_two: _Optional[int] = ..., unknown_four_hundred_eighty_three: _Optional[str] = ...) -> None: ...
    class UnknownTwoHundredFortySeven(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    def __init__(self) -> None: ...

class UnknownTwoHundredFortyNine(_message.Message):
    __slots__ = ("unknown_four_hundred_eighty_four", "unknown_four_hundred_eighty_five")
    class UnknownFourHundredEightyFourEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: int
        def __init__(self, key: _Optional[int] = ..., value: _Optional[int] = ...) -> None: ...
    UNKNOWN_FOUR_HUNDRED_EIGHTY_FOUR_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FOUR_HUNDRED_EIGHTY_FIVE_FIELD_NUMBER: _ClassVar[int]
    unknown_four_hundred_eighty_four: _containers.ScalarMap[int, int]
    unknown_four_hundred_eighty_five: int
    def __init__(self, unknown_four_hundred_eighty_four: _Optional[_Mapping[int, int]] = ..., unknown_four_hundred_eighty_five: _Optional[int] = ...) -> None: ...
