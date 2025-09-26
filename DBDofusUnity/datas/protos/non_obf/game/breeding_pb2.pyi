import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class UnknownSixty(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN_SIXTY_UNSPECIFIED: _ClassVar[UnknownSixty]
    UNKNOWN_SIXTY_1: _ClassVar[UnknownSixty]
    UNKNOWN_SIXTY_2: _ClassVar[UnknownSixty]
    UNKNOWN_SIXTY_3: _ClassVar[UnknownSixty]
    UNKNOWN_SIXTY_4: _ClassVar[UnknownSixty]
    UNKNOWN_SIXTY_5: _ClassVar[UnknownSixty]

class UnknownFiftySeven(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN_FIFTY_SEVEN: _ClassVar[UnknownFiftySeven]

class UnknownThirtyEight(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN_THIRTY_EIGHT: _ClassVar[UnknownThirtyEight]

class UnknownThirtyNine(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN_THIRTY_NINE: _ClassVar[UnknownThirtyNine]

class UnknownForty(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN_FORTY: _ClassVar[UnknownForty]

class UnknownFortyOne(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN_FORTY_ONE: _ClassVar[UnknownFortyOne]

class UnknownFortyThree(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN_FORTY_THREE: _ClassVar[UnknownFortyThree]

class UnknownFortyFour(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN_FORTY_FOUR: _ClassVar[UnknownFortyFour]

class UnknownFortyFive(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN_FORTY_FIVE: _ClassVar[UnknownFortyFive]

class UnknownFortySix(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN_FORTY_SIX: _ClassVar[UnknownFortySix]

class UnknownFortySeven(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN_FORTY_SEVEN: _ClassVar[UnknownFortySeven]

class UnknownFortyEight(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN_FORTY_EIGHT: _ClassVar[UnknownFortyEight]

class UnknownFortyNine(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN_FORTY_NINE: _ClassVar[UnknownFortyNine]

class UnknownFifty(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN_FIFTY: _ClassVar[UnknownFifty]

class UnknownFiftyFour(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN_FIFTY_FOUR: _ClassVar[UnknownFiftyFour]

class UnknownFiftyFive(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN_FIFTY_FIVE: _ClassVar[UnknownFiftyFive]

class UnknownFiftySix(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN_FIFTY_SIX: _ClassVar[UnknownFiftySix]

class UnknownFiftyNine(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN_FIFTY_NINE: _ClassVar[UnknownFiftyNine]
UNKNOWN_SIXTY_UNSPECIFIED: UnknownSixty
UNKNOWN_SIXTY_1: UnknownSixty
UNKNOWN_SIXTY_2: UnknownSixty
UNKNOWN_SIXTY_3: UnknownSixty
UNKNOWN_SIXTY_4: UnknownSixty
UNKNOWN_SIXTY_5: UnknownSixty
UNKNOWN_FIFTY_SEVEN: UnknownFiftySeven
UNKNOWN_THIRTY_EIGHT: UnknownThirtyEight
UNKNOWN_THIRTY_NINE: UnknownThirtyNine
UNKNOWN_FORTY: UnknownForty
UNKNOWN_FORTY_ONE: UnknownFortyOne
UNKNOWN_FORTY_THREE: UnknownFortyThree
UNKNOWN_FORTY_FOUR: UnknownFortyFour
UNKNOWN_FORTY_FIVE: UnknownFortyFive
UNKNOWN_FORTY_SIX: UnknownFortySix
UNKNOWN_FORTY_SEVEN: UnknownFortySeven
UNKNOWN_FORTY_EIGHT: UnknownFortyEight
UNKNOWN_FORTY_NINE: UnknownFortyNine
UNKNOWN_FIFTY: UnknownFifty
UNKNOWN_FIFTY_FOUR: UnknownFiftyFour
UNKNOWN_FIFTY_FIVE: UnknownFiftyFive
UNKNOWN_FIFTY_SIX: UnknownFiftySix
UNKNOWN_FIFTY_NINE: UnknownFiftyNine

class UnknownFortyTwo(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class UnknownFiftyOne(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class UnknownFiftyTwo(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class UnknownFiftyThree(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class UnknownFiftyEight(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class UnknownSixtyOne(_message.Message):
    __slots__ = ("unknown_one_hundred_thirty_nine", "unknown_one_hundred_forty")
    class UnknownOneHundredFortyEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: UnknownSixtyThree
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[UnknownSixtyThree, _Mapping]] = ...) -> None: ...
    UNKNOWN_ONE_HUNDRED_THIRTY_NINE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_ONE_HUNDRED_FORTY_FIELD_NUMBER: _ClassVar[int]
    unknown_one_hundred_thirty_nine: UnknownEightySeven
    unknown_one_hundred_forty: _containers.MessageMap[str, UnknownSixtyThree]
    def __init__(self, unknown_one_hundred_thirty_nine: _Optional[_Union[UnknownEightySeven, _Mapping]] = ..., unknown_one_hundred_forty: _Optional[_Mapping[str, UnknownSixtyThree]] = ...) -> None: ...

class UnknownEightySeven(_message.Message):
    __slots__ = ("unknown_one_hundred_seventy_six", "unknown_one_hundred_seventy_seven", "unknown_one_hundred_seventy_eight")
    class UnknownOneHundredSeventyEightEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: UnknownSixtyThree
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[UnknownSixtyThree, _Mapping]] = ...) -> None: ...
    UNKNOWN_ONE_HUNDRED_SEVENTY_SIX_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_ONE_HUNDRED_SEVENTY_SEVEN_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_ONE_HUNDRED_SEVENTY_EIGHT_FIELD_NUMBER: _ClassVar[int]
    unknown_one_hundred_seventy_six: _containers.RepeatedCompositeFieldContainer[UnknownNinetyThree]
    unknown_one_hundred_seventy_seven: _containers.RepeatedScalarFieldContainer[UnknownFortyNine]
    unknown_one_hundred_seventy_eight: _containers.MessageMap[str, UnknownSixtyThree]
    def __init__(self, unknown_one_hundred_seventy_six: _Optional[_Iterable[_Union[UnknownNinetyThree, _Mapping]]] = ..., unknown_one_hundred_seventy_seven: _Optional[_Iterable[_Union[UnknownFortyNine, str]]] = ..., unknown_one_hundred_seventy_eight: _Optional[_Mapping[str, UnknownSixtyThree]] = ...) -> None: ...

class UnknownNinetyThree(_message.Message):
    __slots__ = ("unknown_one_hundred_eighty_seven", "unknown_one_hundred_eighty_eight")
    UNKNOWN_ONE_HUNDRED_EIGHTY_SEVEN_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_ONE_HUNDRED_EIGHTY_EIGHT_FIELD_NUMBER: _ClassVar[int]
    unknown_one_hundred_eighty_seven: UnknownFiftyFour
    unknown_one_hundred_eighty_eight: int
    def __init__(self, unknown_one_hundred_eighty_seven: _Optional[_Union[UnknownFiftyFour, str]] = ..., unknown_one_hundred_eighty_eight: _Optional[int] = ...) -> None: ...

class UnknownSixtyThree(_message.Message):
    __slots__ = ("unknown_one_hundred_forty_three", "unknown_one_hundred_forty_four", "unknown_one_hundred_forty_five", "unknown_one_hundred_forty_six", "unknown_one_hundred_forty_seven", "unknown_one_hundred_forty_eight", "unknown_one_hundred_forty_nine", "unknown_one_hundred_fifty", "unknown_one_hundred_fifty_one", "unknown_one_hundred_fifty_two", "unknown_one_hundred_fifty_three", "unknown_one_hundred_fifty_four")
    class UnknownSixtyFour(_message.Message):
        __slots__ = ("unknown_one_hundred_forty_two",)
        class UnknownSixtyFive(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            UNKNOWN_SIXTY_FIVE_UNSPECIFIED: _ClassVar[UnknownSixtyThree.UnknownSixtyFour.UnknownSixtyFive]
            UNKNOWN_SIXTY_FIVE_1: _ClassVar[UnknownSixtyThree.UnknownSixtyFour.UnknownSixtyFive]
            UNKNOWN_SIXTY_FIVE_2: _ClassVar[UnknownSixtyThree.UnknownSixtyFour.UnknownSixtyFive]
        UNKNOWN_SIXTY_FIVE_UNSPECIFIED: UnknownSixtyThree.UnknownSixtyFour.UnknownSixtyFive
        UNKNOWN_SIXTY_FIVE_1: UnknownSixtyThree.UnknownSixtyFour.UnknownSixtyFive
        UNKNOWN_SIXTY_FIVE_2: UnknownSixtyThree.UnknownSixtyFour.UnknownSixtyFive
        UNKNOWN_ONE_HUNDRED_FORTY_TWO_FIELD_NUMBER: _ClassVar[int]
        unknown_one_hundred_forty_two: UnknownSixtyThree.UnknownSixtyFour.UnknownSixtyFive
        def __init__(self, unknown_one_hundred_forty_two: _Optional[_Union[UnknownSixtyThree.UnknownSixtyFour.UnknownSixtyFive, str]] = ...) -> None: ...
    class UnknownSixtySix(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    UNKNOWN_ONE_HUNDRED_FORTY_THREE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_ONE_HUNDRED_FORTY_FOUR_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_ONE_HUNDRED_FORTY_FIVE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_ONE_HUNDRED_FORTY_SIX_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_ONE_HUNDRED_FORTY_SEVEN_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_ONE_HUNDRED_FORTY_EIGHT_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_ONE_HUNDRED_FORTY_NINE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_ONE_HUNDRED_FIFTY_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_ONE_HUNDRED_FIFTY_ONE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_ONE_HUNDRED_FIFTY_TWO_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_ONE_HUNDRED_FIFTY_THREE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_ONE_HUNDRED_FIFTY_FOUR_FIELD_NUMBER: _ClassVar[int]
    unknown_one_hundred_forty_three: int
    unknown_one_hundred_forty_four: _containers.RepeatedCompositeFieldContainer[_common_pb2.ObjectEffect]
    unknown_one_hundred_forty_five: int
    unknown_one_hundred_forty_six: bool
    unknown_one_hundred_forty_seven: str
    unknown_one_hundred_forty_eight: _containers.RepeatedCompositeFieldContainer[UnknownSixtyThree.UnknownSixtyFour]
    unknown_one_hundred_forty_nine: bool
    unknown_one_hundred_fifty: _containers.RepeatedScalarFieldContainer[UnknownThirtyNine]
    unknown_one_hundred_fifty_one: UnknownSixtyThree.UnknownSixtySix
    unknown_one_hundred_fifty_two: bool
    unknown_one_hundred_fifty_three: int
    unknown_one_hundred_fifty_four: int
    def __init__(self, unknown_one_hundred_forty_three: _Optional[int] = ..., unknown_one_hundred_forty_four: _Optional[_Iterable[_Union[_common_pb2.ObjectEffect, _Mapping]]] = ..., unknown_one_hundred_forty_five: _Optional[int] = ..., unknown_one_hundred_forty_six: bool = ..., unknown_one_hundred_forty_seven: _Optional[str] = ..., unknown_one_hundred_forty_eight: _Optional[_Iterable[_Union[UnknownSixtyThree.UnknownSixtyFour, _Mapping]]] = ..., unknown_one_hundred_forty_nine: bool = ..., unknown_one_hundred_fifty: _Optional[_Iterable[_Union[UnknownThirtyNine, str]]] = ..., unknown_one_hundred_fifty_one: _Optional[_Union[UnknownSixtyThree.UnknownSixtySix, _Mapping]] = ..., unknown_one_hundred_fifty_two: bool = ..., unknown_one_hundred_fifty_three: _Optional[int] = ..., unknown_one_hundred_fifty_four: _Optional[int] = ...) -> None: ...

class UnknownSixtyTwo(_message.Message):
    __slots__ = ("unknown_one_hundred_forty_one",)
    UNKNOWN_ONE_HUNDRED_FORTY_ONE_FIELD_NUMBER: _ClassVar[int]
    unknown_one_hundred_forty_one: UnknownThirtyEight
    def __init__(self, unknown_one_hundred_forty_one: _Optional[_Union[UnknownThirtyEight, str]] = ...) -> None: ...

class UnknownSixtySeven(_message.Message):
    __slots__ = ("unknown_one_hundred_fifty_five", "unknown_one_hundred_fifty_six")
    UNKNOWN_ONE_HUNDRED_FIFTY_FIVE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_ONE_HUNDRED_FIFTY_SIX_FIELD_NUMBER: _ClassVar[int]
    unknown_one_hundred_fifty_five: str
    unknown_one_hundred_fifty_six: str
    def __init__(self, unknown_one_hundred_fifty_five: _Optional[str] = ..., unknown_one_hundred_fifty_six: _Optional[str] = ...) -> None: ...

class UnknownSixtyEight(_message.Message):
    __slots__ = ("unknown_one_hundred_fifty_seven",)
    UNKNOWN_ONE_HUNDRED_FIFTY_SEVEN_FIELD_NUMBER: _ClassVar[int]
    unknown_one_hundred_fifty_seven: UnknownForty
    def __init__(self, unknown_one_hundred_fifty_seven: _Optional[_Union[UnknownForty, str]] = ...) -> None: ...

class PaddockInformationEvent(_message.Message):
    __slots__ = ("unknown_one_hundred_twenty_eight", "unknown_one_hundred_thirty", "unknown_one_hundred_thirty_one")
    class UnknownThirtyThree(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN_THIRTY_THREE_UNSPECIFIED: _ClassVar[PaddockInformationEvent.UnknownThirtyThree]
        UNKNOWN_THIRTY_THREE_1: _ClassVar[PaddockInformationEvent.UnknownThirtyThree]
        UNKNOWN_THIRTY_THREE_2: _ClassVar[PaddockInformationEvent.UnknownThirtyThree]
    UNKNOWN_THIRTY_THREE_UNSPECIFIED: PaddockInformationEvent.UnknownThirtyThree
    UNKNOWN_THIRTY_THREE_1: PaddockInformationEvent.UnknownThirtyThree
    UNKNOWN_THIRTY_THREE_2: PaddockInformationEvent.UnknownThirtyThree
    class UnknownThirtyFour(_message.Message):
        __slots__ = ("unknown_one_hundred_twenty_six", "unknown_one_hundred_twenty_seven")
        class UnknownThirtyFive(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            UNKNOWN_THIRTY_FIVE_UNSPECIFIED: _ClassVar[PaddockInformationEvent.UnknownThirtyFour.UnknownThirtyFive]
        UNKNOWN_THIRTY_FIVE_UNSPECIFIED: PaddockInformationEvent.UnknownThirtyFour.UnknownThirtyFive
        UNKNOWN_ONE_HUNDRED_TWENTY_SIX_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_ONE_HUNDRED_TWENTY_SEVEN_FIELD_NUMBER: _ClassVar[int]
        unknown_one_hundred_twenty_six: PaddockInformationEvent.UnknownThirtyFour.UnknownThirtyFive
        unknown_one_hundred_twenty_seven: UnknownEightySeven
        def __init__(self, unknown_one_hundred_twenty_six: _Optional[_Union[PaddockInformationEvent.UnknownThirtyFour.UnknownThirtyFive, str]] = ..., unknown_one_hundred_twenty_seven: _Optional[_Union[UnknownEightySeven, _Mapping]] = ...) -> None: ...
    UNKNOWN_ONE_HUNDRED_TWENTY_EIGHT_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_ONE_HUNDRED_THIRTY_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_ONE_HUNDRED_THIRTY_ONE_FIELD_NUMBER: _ClassVar[int]
    unknown_one_hundred_twenty_eight: int
    unknown_one_hundred_thirty: PaddockInformationEvent.UnknownThirtyThree
    unknown_one_hundred_thirty_one: PaddockInformationEvent.UnknownThirtyFour
    def __init__(self, unknown_one_hundred_twenty_eight: _Optional[int] = ..., unknown_one_hundred_thirty: _Optional[_Union[PaddockInformationEvent.UnknownThirtyThree, str]] = ..., unknown_one_hundred_thirty_one: _Optional[_Union[PaddockInformationEvent.UnknownThirtyFour, _Mapping]] = ...) -> None: ...

class UnknownSixtyNine(_message.Message):
    __slots__ = ("unknown_one_hundred_fifty_eight", "unknown_one_hundred_fifty_nine")
    class UnknownSeventy(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    UNKNOWN_ONE_HUNDRED_FIFTY_EIGHT_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_ONE_HUNDRED_FIFTY_NINE_FIELD_NUMBER: _ClassVar[int]
    unknown_one_hundred_fifty_eight: UnknownSixtyNine.UnknownSeventy
    unknown_one_hundred_fifty_nine: UnknownFortyOne
    def __init__(self, unknown_one_hundred_fifty_eight: _Optional[_Union[UnknownSixtyNine.UnknownSeventy, _Mapping]] = ..., unknown_one_hundred_fifty_nine: _Optional[_Union[UnknownFortyOne, str]] = ...) -> None: ...

class PaddockInformationRequest(_message.Message):
    __slots__ = ("unknown_one_hundred_thirty_two",)
    UNKNOWN_ONE_HUNDRED_THIRTY_TWO_FIELD_NUMBER: _ClassVar[int]
    unknown_one_hundred_thirty_two: int
    def __init__(self, unknown_one_hundred_thirty_two: _Optional[int] = ...) -> None: ...

class UnknownSeventyOne(_message.Message):
    __slots__ = ("unknown_one_hundred_sixty", "unknown_one_hundred_sixty_one")
    class UnknownSeventyTwo(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class UnknownSeventyThree(_message.Message):
        __slots__ = ()
        class UnknownSeventyFour(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            UNKNOWN_SEVENTY_FOUR_UNSPECIFIED: _ClassVar[UnknownSeventyOne.UnknownSeventyThree.UnknownSeventyFour]
            UNKNOWN_SEVENTY_FOUR_1: _ClassVar[UnknownSeventyOne.UnknownSeventyThree.UnknownSeventyFour]
            UNKNOWN_SEVENTY_FOUR_2: _ClassVar[UnknownSeventyOne.UnknownSeventyThree.UnknownSeventyFour]
            UNKNOWN_SEVENTY_FOUR_3: _ClassVar[UnknownSeventyOne.UnknownSeventyThree.UnknownSeventyFour]
            UNKNOWN_SEVENTY_FOUR_4: _ClassVar[UnknownSeventyOne.UnknownSeventyThree.UnknownSeventyFour]
            UNKNOWN_SEVENTY_FOUR_5: _ClassVar[UnknownSeventyOne.UnknownSeventyThree.UnknownSeventyFour]
        UNKNOWN_SEVENTY_FOUR_UNSPECIFIED: UnknownSeventyOne.UnknownSeventyThree.UnknownSeventyFour
        UNKNOWN_SEVENTY_FOUR_1: UnknownSeventyOne.UnknownSeventyThree.UnknownSeventyFour
        UNKNOWN_SEVENTY_FOUR_2: UnknownSeventyOne.UnknownSeventyThree.UnknownSeventyFour
        UNKNOWN_SEVENTY_FOUR_3: UnknownSeventyOne.UnknownSeventyThree.UnknownSeventyFour
        UNKNOWN_SEVENTY_FOUR_4: UnknownSeventyOne.UnknownSeventyThree.UnknownSeventyFour
        UNKNOWN_SEVENTY_FOUR_5: UnknownSeventyOne.UnknownSeventyThree.UnknownSeventyFour
        def __init__(self) -> None: ...
    class UnknownSeventyFive(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class UnknownSeventySix(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    UNKNOWN_ONE_HUNDRED_SIXTY_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_ONE_HUNDRED_SIXTY_ONE_FIELD_NUMBER: _ClassVar[int]
    unknown_one_hundred_sixty: UnknownSeventyOne.UnknownSeventyTwo
    unknown_one_hundred_sixty_one: UnknownFortyThree
    def __init__(self, unknown_one_hundred_sixty: _Optional[_Union[UnknownSeventyOne.UnknownSeventyTwo, _Mapping]] = ..., unknown_one_hundred_sixty_one: _Optional[_Union[UnknownFortyThree, str]] = ...) -> None: ...

class UnknownSeventySeven(_message.Message):
    __slots__ = ("unknown_one_hundred_sixty_two", "unknown_one_hundred_sixty_three", "unknown_one_hundred_sixty_four", "unknown_one_hundred_sixty_five")
    UNKNOWN_ONE_HUNDRED_SIXTY_TWO_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_ONE_HUNDRED_SIXTY_THREE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_ONE_HUNDRED_SIXTY_FOUR_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_ONE_HUNDRED_SIXTY_FIVE_FIELD_NUMBER: _ClassVar[int]
    unknown_one_hundred_sixty_two: str
    unknown_one_hundred_sixty_three: str
    unknown_one_hundred_sixty_four: int
    unknown_one_hundred_sixty_five: str
    def __init__(self, unknown_one_hundred_sixty_two: _Optional[str] = ..., unknown_one_hundred_sixty_three: _Optional[str] = ..., unknown_one_hundred_sixty_four: _Optional[int] = ..., unknown_one_hundred_sixty_five: _Optional[str] = ...) -> None: ...

class UnknownSeventyEight(_message.Message):
    __slots__ = ("unknown_one_hundred_sixty_six",)
    UNKNOWN_ONE_HUNDRED_SIXTY_SIX_FIELD_NUMBER: _ClassVar[int]
    unknown_one_hundred_sixty_six: int
    def __init__(self, unknown_one_hundred_sixty_six: _Optional[int] = ...) -> None: ...

class PaddockMountAddRequest(_message.Message):
    __slots__ = ("object_uids", "unknown_one_hundred_thirty_three")
    OBJECT_UIDS_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_ONE_HUNDRED_THIRTY_THREE_FIELD_NUMBER: _ClassVar[int]
    object_uids: _containers.RepeatedScalarFieldContainer[int]
    unknown_one_hundred_thirty_three: UnknownFortyFour
    def __init__(self, object_uids: _Optional[_Iterable[int]] = ..., unknown_one_hundred_thirty_three: _Optional[_Union[UnknownFortyFour, str]] = ...) -> None: ...

class UnknownSeventyNine(_message.Message):
    __slots__ = ("unknown_one_hundred_sixty_seven", "unknown_one_hundred_sixty_eight")
    class UnknownEighty(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    UNKNOWN_ONE_HUNDRED_SIXTY_SEVEN_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_ONE_HUNDRED_SIXTY_EIGHT_FIELD_NUMBER: _ClassVar[int]
    unknown_one_hundred_sixty_seven: UnknownSeventyNine.UnknownEighty
    unknown_one_hundred_sixty_eight: UnknownFortyFive
    def __init__(self, unknown_one_hundred_sixty_seven: _Optional[_Union[UnknownSeventyNine.UnknownEighty, _Mapping]] = ..., unknown_one_hundred_sixty_eight: _Optional[_Union[UnknownFortyFive, str]] = ...) -> None: ...

class UnknownEightyOne(_message.Message):
    __slots__ = ("unknown_one_hundred_sixty_nine", "unknown_one_hundred_seventy")
    UNKNOWN_ONE_HUNDRED_SIXTY_NINE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_ONE_HUNDRED_SEVENTY_FIELD_NUMBER: _ClassVar[int]
    unknown_one_hundred_sixty_nine: UnknownFortySix
    unknown_one_hundred_seventy: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, unknown_one_hundred_sixty_nine: _Optional[_Union[UnknownFortySix, str]] = ..., unknown_one_hundred_seventy: _Optional[_Iterable[str]] = ...) -> None: ...

class UnknownEightyTwo(_message.Message):
    __slots__ = ("unknown_one_hundred_seventy_one", "unknown_one_hundred_seventy_two")
    class UnknownEightyThree(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    UNKNOWN_ONE_HUNDRED_SEVENTY_ONE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_ONE_HUNDRED_SEVENTY_TWO_FIELD_NUMBER: _ClassVar[int]
    unknown_one_hundred_seventy_one: UnknownFortySeven
    unknown_one_hundred_seventy_two: UnknownEightyTwo.UnknownEightyThree
    def __init__(self, unknown_one_hundred_seventy_one: _Optional[_Union[UnknownFortySeven, str]] = ..., unknown_one_hundred_seventy_two: _Optional[_Union[UnknownEightyTwo.UnknownEightyThree, _Mapping]] = ...) -> None: ...

class UnknownEightyFour(_message.Message):
    __slots__ = ("unknown_one_hundred_seventy_three",)
    UNKNOWN_ONE_HUNDRED_SEVENTY_THREE_FIELD_NUMBER: _ClassVar[int]
    unknown_one_hundred_seventy_three: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, unknown_one_hundred_seventy_three: _Optional[_Iterable[str]] = ...) -> None: ...

class UnknownEightyFive(_message.Message):
    __slots__ = ("unknown_one_hundred_seventy_four",)
    class UnknownOneHundredSeventyFourEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: bool
        def __init__(self, key: _Optional[int] = ..., value: bool = ...) -> None: ...
    UNKNOWN_ONE_HUNDRED_SEVENTY_FOUR_FIELD_NUMBER: _ClassVar[int]
    unknown_one_hundred_seventy_four: _containers.ScalarMap[int, bool]
    def __init__(self, unknown_one_hundred_seventy_four: _Optional[_Mapping[int, bool]] = ...) -> None: ...

class UnknownEightySix(_message.Message):
    __slots__ = ("unknown_one_hundred_seventy_five",)
    UNKNOWN_ONE_HUNDRED_SEVENTY_FIVE_FIELD_NUMBER: _ClassVar[int]
    unknown_one_hundred_seventy_five: UnknownFortyEight
    def __init__(self, unknown_one_hundred_seventy_five: _Optional[_Union[UnknownFortyEight, str]] = ...) -> None: ...

class UnknownEightyEight(_message.Message):
    __slots__ = ("unknown_one_hundred_seventy_nine", "unknown_one_hundred_eighty")
    class UnknownEightyNine(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    UNKNOWN_ONE_HUNDRED_SEVENTY_NINE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_ONE_HUNDRED_EIGHTY_FIELD_NUMBER: _ClassVar[int]
    unknown_one_hundred_seventy_nine: UnknownFifty
    unknown_one_hundred_eighty: UnknownEightyEight.UnknownEightyNine
    def __init__(self, unknown_one_hundred_seventy_nine: _Optional[_Union[UnknownFifty, str]] = ..., unknown_one_hundred_eighty: _Optional[_Union[UnknownEightyEight.UnknownEightyNine, _Mapping]] = ...) -> None: ...

class UnknownNinety(_message.Message):
    __slots__ = ("unknown_one_hundred_eighty_one",)
    class UnknownOneHundredEightyOneEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: UnknownFiftyOne
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[UnknownFiftyOne, _Mapping]] = ...) -> None: ...
    UNKNOWN_ONE_HUNDRED_EIGHTY_ONE_FIELD_NUMBER: _ClassVar[int]
    unknown_one_hundred_eighty_one: _containers.MessageMap[str, UnknownFiftyOne]
    def __init__(self, unknown_one_hundred_eighty_one: _Optional[_Mapping[str, UnknownFiftyOne]] = ...) -> None: ...

class UnknownNinetyOne(_message.Message):
    __slots__ = ("unknown_one_hundred_eighty_two",)
    class UnknownOneHundredEightyTwoEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: int
        def __init__(self, key: _Optional[int] = ..., value: _Optional[int] = ...) -> None: ...
    UNKNOWN_ONE_HUNDRED_EIGHTY_TWO_FIELD_NUMBER: _ClassVar[int]
    unknown_one_hundred_eighty_two: _containers.ScalarMap[int, int]
    def __init__(self, unknown_one_hundred_eighty_two: _Optional[_Mapping[int, int]] = ...) -> None: ...

class MountBoostResponse(_message.Message):
    __slots__ = ("unknown_one_hundred_twenty_four", "unknown_one_hundred_twenty_five")
    class UnknownThirtyOne(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN_THIRTY_ONE_UNSPECIFIED: _ClassVar[MountBoostResponse.UnknownThirtyOne]
        UNKNOWN_THIRTY_ONE_1: _ClassVar[MountBoostResponse.UnknownThirtyOne]
        UNKNOWN_THIRTY_ONE_2: _ClassVar[MountBoostResponse.UnknownThirtyOne]
        UNKNOWN_THIRTY_ONE_3: _ClassVar[MountBoostResponse.UnknownThirtyOne]
    UNKNOWN_THIRTY_ONE_UNSPECIFIED: MountBoostResponse.UnknownThirtyOne
    UNKNOWN_THIRTY_ONE_1: MountBoostResponse.UnknownThirtyOne
    UNKNOWN_THIRTY_ONE_2: MountBoostResponse.UnknownThirtyOne
    UNKNOWN_THIRTY_ONE_3: MountBoostResponse.UnknownThirtyOne
    class UnknownThirtyTwo(_message.Message):
        __slots__ = ("unknown_one_hundred_twenty_three",)
        UNKNOWN_ONE_HUNDRED_TWENTY_THREE_FIELD_NUMBER: _ClassVar[int]
        unknown_one_hundred_twenty_three: _containers.RepeatedScalarFieldContainer[UnknownSixty]
        def __init__(self, unknown_one_hundred_twenty_three: _Optional[_Iterable[_Union[UnknownSixty, str]]] = ...) -> None: ...
    UNKNOWN_ONE_HUNDRED_TWENTY_FOUR_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_ONE_HUNDRED_TWENTY_FIVE_FIELD_NUMBER: _ClassVar[int]
    unknown_one_hundred_twenty_four: MountBoostResponse.UnknownThirtyTwo
    unknown_one_hundred_twenty_five: MountBoostResponse.UnknownThirtyOne
    def __init__(self, unknown_one_hundred_twenty_four: _Optional[_Union[MountBoostResponse.UnknownThirtyTwo, _Mapping]] = ..., unknown_one_hundred_twenty_five: _Optional[_Union[MountBoostResponse.UnknownThirtyOne, str]] = ...) -> None: ...

class UnknownNinetyTwo(_message.Message):
    __slots__ = ("unknown_one_hundred_eighty_three", "unknown_one_hundred_eighty_four", "unknown_one_hundred_eighty_five", "unknown_one_hundred_eighty_six")
    UNKNOWN_ONE_HUNDRED_EIGHTY_THREE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_ONE_HUNDRED_EIGHTY_FOUR_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_ONE_HUNDRED_EIGHTY_FIVE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_ONE_HUNDRED_EIGHTY_SIX_FIELD_NUMBER: _ClassVar[int]
    unknown_one_hundred_eighty_three: str
    unknown_one_hundred_eighty_four: int
    unknown_one_hundred_eighty_five: str
    unknown_one_hundred_eighty_six: str
    def __init__(self, unknown_one_hundred_eighty_three: _Optional[str] = ..., unknown_one_hundred_eighty_four: _Optional[int] = ..., unknown_one_hundred_eighty_five: _Optional[str] = ..., unknown_one_hundred_eighty_six: _Optional[str] = ...) -> None: ...

class PaddockMountsUpdateEvent(_message.Message):
    __slots__ = ("unknown_one_hundred_thirty_six", "unknown_one_hundred_thirty_seven")
    class UnknownOneHundredThirtySixEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: UnknownFiftyTwo
        def __init__(self, key: _Optional[int] = ..., value: _Optional[_Union[UnknownFiftyTwo, _Mapping]] = ...) -> None: ...
    class UnknownOneHundredThirtySevenEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: UnknownFiftyThree
        def __init__(self, key: _Optional[int] = ..., value: _Optional[_Union[UnknownFiftyThree, _Mapping]] = ...) -> None: ...
    UNKNOWN_ONE_HUNDRED_THIRTY_SIX_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_ONE_HUNDRED_THIRTY_SEVEN_FIELD_NUMBER: _ClassVar[int]
    unknown_one_hundred_thirty_six: _containers.MessageMap[int, UnknownFiftyTwo]
    unknown_one_hundred_thirty_seven: _containers.MessageMap[int, UnknownFiftyThree]
    def __init__(self, unknown_one_hundred_thirty_six: _Optional[_Mapping[int, UnknownFiftyTwo]] = ..., unknown_one_hundred_thirty_seven: _Optional[_Mapping[int, UnknownFiftyThree]] = ...) -> None: ...

class UnknownNinetyFour(_message.Message):
    __slots__ = ("unknown_one_hundred_eighty_nine",)
    UNKNOWN_ONE_HUNDRED_EIGHTY_NINE_FIELD_NUMBER: _ClassVar[int]
    unknown_one_hundred_eighty_nine: UnknownEightySeven
    def __init__(self, unknown_one_hundred_eighty_nine: _Optional[_Union[UnknownEightySeven, _Mapping]] = ...) -> None: ...

class UnknownNinetyFive(_message.Message):
    __slots__ = ("unknown_one_hundred_ninety",)
    class UnknownOneHundredNinetyEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: int
        def __init__(self, key: _Optional[int] = ..., value: _Optional[int] = ...) -> None: ...
    UNKNOWN_ONE_HUNDRED_NINETY_FIELD_NUMBER: _ClassVar[int]
    unknown_one_hundred_ninety: _containers.ScalarMap[int, int]
    def __init__(self, unknown_one_hundred_ninety: _Optional[_Mapping[int, int]] = ...) -> None: ...

class UnknownNinetySix(_message.Message):
    __slots__ = ("unknown_one_hundred_ninety_one", "unknown_one_hundred_ninety_two", "unknown_one_hundred_ninety_three")
    UNKNOWN_ONE_HUNDRED_NINETY_ONE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_ONE_HUNDRED_NINETY_TWO_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_ONE_HUNDRED_NINETY_THREE_FIELD_NUMBER: _ClassVar[int]
    unknown_one_hundred_ninety_one: _containers.RepeatedScalarFieldContainer[str]
    unknown_one_hundred_ninety_two: UnknownFiftyFive
    unknown_one_hundred_ninety_three: str
    def __init__(self, unknown_one_hundred_ninety_one: _Optional[_Iterable[str]] = ..., unknown_one_hundred_ninety_two: _Optional[_Union[UnknownFiftyFive, str]] = ..., unknown_one_hundred_ninety_three: _Optional[str] = ...) -> None: ...

class UnknownNinetySeven(_message.Message):
    __slots__ = ("unknown_one_hundred_ninety_four",)
    class UnknownNinetyEight(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    UNKNOWN_ONE_HUNDRED_NINETY_FOUR_FIELD_NUMBER: _ClassVar[int]
    unknown_one_hundred_ninety_four: UnknownNinetySeven.UnknownNinetyEight
    def __init__(self, unknown_one_hundred_ninety_four: _Optional[_Union[UnknownNinetySeven.UnknownNinetyEight, _Mapping]] = ...) -> None: ...

class MountBoostRequest(_message.Message):
    __slots__ = ("unknown_one_hundred_twenty_two",)
    UNKNOWN_ONE_HUNDRED_TWENTY_TWO_FIELD_NUMBER: _ClassVar[int]
    unknown_one_hundred_twenty_two: UnknownFiftySeven
    def __init__(self, unknown_one_hundred_twenty_two: _Optional[_Union[UnknownFiftySeven, str]] = ...) -> None: ...

class UnknownNinetyNine(_message.Message):
    __slots__ = ("unknown_one_hundred_ninety_five",)
    class UnknownOneHundredNinetyFiveEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: UnknownFiftyEight
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[UnknownFiftyEight, _Mapping]] = ...) -> None: ...
    UNKNOWN_ONE_HUNDRED_NINETY_FIVE_FIELD_NUMBER: _ClassVar[int]
    unknown_one_hundred_ninety_five: _containers.MessageMap[str, UnknownFiftyEight]
    def __init__(self, unknown_one_hundred_ninety_five: _Optional[_Mapping[str, UnknownFiftyEight]] = ...) -> None: ...

class PaddockSlotsEvent(_message.Message):
    __slots__ = ("unknown_one_hundred_thirty_eight",)
    class UnknownOneHundredThirtyEightEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: bool
        def __init__(self, key: _Optional[int] = ..., value: bool = ...) -> None: ...
    UNKNOWN_ONE_HUNDRED_THIRTY_EIGHT_FIELD_NUMBER: _ClassVar[int]
    unknown_one_hundred_thirty_eight: _containers.ScalarMap[int, bool]
    def __init__(self, unknown_one_hundred_thirty_eight: _Optional[_Mapping[int, bool]] = ...) -> None: ...

class UnknownOneHundred(_message.Message):
    __slots__ = ("unknown_one_hundred_ninety_six", "unknown_one_hundred_ninety_seven", "unknown_one_hundred_ninety_eight")
    UNKNOWN_ONE_HUNDRED_NINETY_SIX_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_ONE_HUNDRED_NINETY_SEVEN_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_ONE_HUNDRED_NINETY_EIGHT_FIELD_NUMBER: _ClassVar[int]
    unknown_one_hundred_ninety_six: str
    unknown_one_hundred_ninety_seven: UnknownFiftyNine
    unknown_one_hundred_ninety_eight: str
    def __init__(self, unknown_one_hundred_ninety_six: _Optional[str] = ..., unknown_one_hundred_ninety_seven: _Optional[_Union[UnknownFiftyNine, str]] = ..., unknown_one_hundred_ninety_eight: _Optional[str] = ...) -> None: ...

class PaddockMountsEvent(_message.Message):
    __slots__ = ("unknown_one_hundred_thirty_five",)
    class UnknownThirtySix(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN_THIRTY_SIX_UNSPECIFIED: _ClassVar[PaddockMountsEvent.UnknownThirtySix]
    UNKNOWN_THIRTY_SIX_UNSPECIFIED: PaddockMountsEvent.UnknownThirtySix
    class UnknownThirtySeven(_message.Message):
        __slots__ = ("unknown_one_hundred_thirty_four",)
        class UnknownOneHundredThirtyFourEntry(_message.Message):
            __slots__ = ("key", "value")
            KEY_FIELD_NUMBER: _ClassVar[int]
            VALUE_FIELD_NUMBER: _ClassVar[int]
            key: str
            value: UnknownSixtyThree
            def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[UnknownSixtyThree, _Mapping]] = ...) -> None: ...
        UNKNOWN_ONE_HUNDRED_THIRTY_FOUR_FIELD_NUMBER: _ClassVar[int]
        unknown_one_hundred_thirty_four: _containers.MessageMap[str, UnknownSixtyThree]
        def __init__(self, unknown_one_hundred_thirty_four: _Optional[_Mapping[str, UnknownSixtyThree]] = ...) -> None: ...
    UNKNOWN_ONE_HUNDRED_THIRTY_FIVE_FIELD_NUMBER: _ClassVar[int]
    unknown_one_hundred_thirty_five: PaddockMountsEvent.UnknownThirtySeven
    def __init__(self, unknown_one_hundred_thirty_five: _Optional[_Union[PaddockMountsEvent.UnknownThirtySeven, _Mapping]] = ...) -> None: ...

class PaddockListenStartRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class PaddockSlotsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class PaddockListenStopRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class PaddockListenStopEvent(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
