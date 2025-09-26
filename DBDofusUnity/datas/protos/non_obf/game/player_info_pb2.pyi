import common_pb2 as _common_pb2
import preset_pb2 as _preset_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class UnknownFourHundredFortyEight(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN_FOUR_HUNDRED_FORTY_EIGHT_UNSPECIFIED: _ClassVar[UnknownFourHundredFortyEight]
    UNKNOWN_FOUR_HUNDRED_FORTY_EIGHT_1: _ClassVar[UnknownFourHundredFortyEight]

class UnknownFourHundredFortySix(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN_FOUR_HUNDRED_FORTY_SIX_UNSPECIFIED: _ClassVar[UnknownFourHundredFortySix]
    UNKNOWN_FOUR_HUNDRED_FORTY_SIX_1: _ClassVar[UnknownFourHundredFortySix]
    UNKNOWN_FOUR_HUNDRED_FORTY_SIX_2: _ClassVar[UnknownFourHundredFortySix]

class UnknownFourHundredFortySeven(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN_FOUR_HUNDRED_FORTY_SEVEN_UNSPECIFIED: _ClassVar[UnknownFourHundredFortySeven]
    UNKNOWN_FOUR_HUNDRED_FORTY_SEVEN_1: _ClassVar[UnknownFourHundredFortySeven]
    UNKNOWN_FOUR_HUNDRED_FORTY_SEVEN_2: _ClassVar[UnknownFourHundredFortySeven]

class UnknownFourHundredFortyThree(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN_FOUR_HUNDRED_FORTY_THREE: _ClassVar[UnknownFourHundredFortyThree]

class UnknownFourHundredFortyFive(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN_FOUR_HUNDRED_FORTY_FIVE: _ClassVar[UnknownFourHundredFortyFive]
UNKNOWN_FOUR_HUNDRED_FORTY_EIGHT_UNSPECIFIED: UnknownFourHundredFortyEight
UNKNOWN_FOUR_HUNDRED_FORTY_EIGHT_1: UnknownFourHundredFortyEight
UNKNOWN_FOUR_HUNDRED_FORTY_SIX_UNSPECIFIED: UnknownFourHundredFortySix
UNKNOWN_FOUR_HUNDRED_FORTY_SIX_1: UnknownFourHundredFortySix
UNKNOWN_FOUR_HUNDRED_FORTY_SIX_2: UnknownFourHundredFortySix
UNKNOWN_FOUR_HUNDRED_FORTY_SEVEN_UNSPECIFIED: UnknownFourHundredFortySeven
UNKNOWN_FOUR_HUNDRED_FORTY_SEVEN_1: UnknownFourHundredFortySeven
UNKNOWN_FOUR_HUNDRED_FORTY_SEVEN_2: UnknownFourHundredFortySeven
UNKNOWN_FOUR_HUNDRED_FORTY_THREE: UnknownFourHundredFortyThree
UNKNOWN_FOUR_HUNDRED_FORTY_FIVE: UnknownFourHundredFortyFive

class UnknownFourHundredFortyFour(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class UnknownFourHundredFortyNine(_message.Message):
    __slots__ = ("unknown_seven_hundred_eighty_two", "unknown_seven_hundred_eighty_three")
    class UnknownFourHundredFifty(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class UnknownFourHundredFiftyOne(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    UNKNOWN_SEVEN_HUNDRED_EIGHTY_TWO_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_SEVEN_HUNDRED_EIGHTY_THREE_FIELD_NUMBER: _ClassVar[int]
    unknown_seven_hundred_eighty_two: UnknownFourHundredFortyNine.UnknownFourHundredFifty
    unknown_seven_hundred_eighty_three: UnknownFourHundredFortyNine.UnknownFourHundredFiftyOne
    def __init__(self, unknown_seven_hundred_eighty_two: _Optional[_Union[UnknownFourHundredFortyNine.UnknownFourHundredFifty, _Mapping]] = ..., unknown_seven_hundred_eighty_three: _Optional[_Union[UnknownFourHundredFortyNine.UnknownFourHundredFiftyOne, _Mapping]] = ...) -> None: ...

class UnknownFourHundredFiftyTwo(_message.Message):
    __slots__ = ("unknown_seven_hundred_eighty_four", "unknown_seven_hundred_eighty_five")
    class UnknownFourHundredFiftyThree(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class UnknownFourHundredFiftyFour(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    UNKNOWN_SEVEN_HUNDRED_EIGHTY_FOUR_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_SEVEN_HUNDRED_EIGHTY_FIVE_FIELD_NUMBER: _ClassVar[int]
    unknown_seven_hundred_eighty_four: UnknownFourHundredFiftyTwo.UnknownFourHundredFiftyFour
    unknown_seven_hundred_eighty_five: UnknownFourHundredFiftyTwo.UnknownFourHundredFiftyThree
    def __init__(self, unknown_seven_hundred_eighty_four: _Optional[_Union[UnknownFourHundredFiftyTwo.UnknownFourHundredFiftyFour, _Mapping]] = ..., unknown_seven_hundred_eighty_five: _Optional[_Union[UnknownFourHundredFiftyTwo.UnknownFourHundredFiftyThree, _Mapping]] = ...) -> None: ...

class UnknownFourHundredFiftyFive(_message.Message):
    __slots__ = ("unknown_seven_hundred_eighty_six",)
    UNKNOWN_SEVEN_HUNDRED_EIGHTY_SIX_FIELD_NUMBER: _ClassVar[int]
    unknown_seven_hundred_eighty_six: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, unknown_seven_hundred_eighty_six: _Optional[_Iterable[int]] = ...) -> None: ...

class UnknownFourHundredFiftySix(_message.Message):
    __slots__ = ("unknown_seven_hundred_eighty_seven", "unknown_seven_hundred_eighty_eight")
    class UnknownFourHundredFiftySeven(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class UnknownFourHundredFiftyEight(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    UNKNOWN_SEVEN_HUNDRED_EIGHTY_SEVEN_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_SEVEN_HUNDRED_EIGHTY_EIGHT_FIELD_NUMBER: _ClassVar[int]
    unknown_seven_hundred_eighty_seven: UnknownFourHundredFiftySix.UnknownFourHundredFiftyEight
    unknown_seven_hundred_eighty_eight: UnknownFourHundredFiftySix.UnknownFourHundredFiftySeven
    def __init__(self, unknown_seven_hundred_eighty_seven: _Optional[_Union[UnknownFourHundredFiftySix.UnknownFourHundredFiftyEight, _Mapping]] = ..., unknown_seven_hundred_eighty_eight: _Optional[_Union[UnknownFourHundredFiftySix.UnknownFourHundredFiftySeven, _Mapping]] = ...) -> None: ...

class UnknownFourHundredFiftyNine(_message.Message):
    __slots__ = ("unknown_seven_hundred_eighty_nine",)
    UNKNOWN_SEVEN_HUNDRED_EIGHTY_NINE_FIELD_NUMBER: _ClassVar[int]
    unknown_seven_hundred_eighty_nine: _containers.RepeatedScalarFieldContainer[UnknownFourHundredFortyThree]
    def __init__(self, unknown_seven_hundred_eighty_nine: _Optional[_Iterable[_Union[UnknownFourHundredFortyThree, str]]] = ...) -> None: ...

class UnknownFourHundredSixty(_message.Message):
    __slots__ = ("unknown_eight_hundred_twenty_four", "unknown_eight_hundred_twenty_five")
    class UnknownFourHundredSixtyOne(_message.Message):
        __slots__ = ()
        class UnknownFourHundredSixtyTwo(_message.Message):
            __slots__ = ()
            def __init__(self) -> None: ...
        def __init__(self) -> None: ...
    class UnknownFourHundredSixtyThree(_message.Message):
        __slots__ = ()
        class UnknownFourHundredSixtyFour(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            UNKNOWN_FOUR_HUNDRED_SIXTY_FOUR_UNSPECIFIED: _ClassVar[UnknownFourHundredSixty.UnknownFourHundredSixtyThree.UnknownFourHundredSixtyFour]
            UNKNOWN_FOUR_HUNDRED_SIXTY_FOUR_1: _ClassVar[UnknownFourHundredSixty.UnknownFourHundredSixtyThree.UnknownFourHundredSixtyFour]
            UNKNOWN_FOUR_HUNDRED_SIXTY_FOUR_2: _ClassVar[UnknownFourHundredSixty.UnknownFourHundredSixtyThree.UnknownFourHundredSixtyFour]
        UNKNOWN_FOUR_HUNDRED_SIXTY_FOUR_UNSPECIFIED: UnknownFourHundredSixty.UnknownFourHundredSixtyThree.UnknownFourHundredSixtyFour
        UNKNOWN_FOUR_HUNDRED_SIXTY_FOUR_1: UnknownFourHundredSixty.UnknownFourHundredSixtyThree.UnknownFourHundredSixtyFour
        UNKNOWN_FOUR_HUNDRED_SIXTY_FOUR_2: UnknownFourHundredSixty.UnknownFourHundredSixtyThree.UnknownFourHundredSixtyFour
        def __init__(self) -> None: ...
    class UnknownFourHundredSixtyFive(_message.Message):
        __slots__ = ("unknown_seven_hundred_ninety_nine", "unknown_eight_hundred", "unknown_eight_hundred_one", "unknown_eight_hundred_two", "unknown_eight_hundred_three", "unknown_eight_hundred_four", "unknown_eight_hundred_five", "unknown_eight_hundred_six")
        class UnknownEightHundredOneEntry(_message.Message):
            __slots__ = ("key", "value")
            KEY_FIELD_NUMBER: _ClassVar[int]
            VALUE_FIELD_NUMBER: _ClassVar[int]
            key: int
            value: int
            def __init__(self, key: _Optional[int] = ..., value: _Optional[int] = ...) -> None: ...
        class UnknownFourHundredSixtySix(_message.Message):
            __slots__ = ("unknown_seven_hundred_ninety", "unknown_seven_hundred_ninety_one")
            UNKNOWN_SEVEN_HUNDRED_NINETY_FIELD_NUMBER: _ClassVar[int]
            UNKNOWN_SEVEN_HUNDRED_NINETY_ONE_FIELD_NUMBER: _ClassVar[int]
            unknown_seven_hundred_ninety: int
            unknown_seven_hundred_ninety_one: str
            def __init__(self, unknown_seven_hundred_ninety: _Optional[int] = ..., unknown_seven_hundred_ninety_one: _Optional[str] = ...) -> None: ...
        class UnknownFourHundredSixtySeven(_message.Message):
            __slots__ = ("unknown_seven_hundred_ninety_two", "unknown_seven_hundred_ninety_three", "unknown_seven_hundred_ninety_four")
            UNKNOWN_SEVEN_HUNDRED_NINETY_TWO_FIELD_NUMBER: _ClassVar[int]
            UNKNOWN_SEVEN_HUNDRED_NINETY_THREE_FIELD_NUMBER: _ClassVar[int]
            UNKNOWN_SEVEN_HUNDRED_NINETY_FOUR_FIELD_NUMBER: _ClassVar[int]
            unknown_seven_hundred_ninety_two: int
            unknown_seven_hundred_ninety_three: _common_pb2.SocialEmblem
            unknown_seven_hundred_ninety_four: str
            def __init__(self, unknown_seven_hundred_ninety_two: _Optional[int] = ..., unknown_seven_hundred_ninety_three: _Optional[_Union[_common_pb2.SocialEmblem, _Mapping]] = ..., unknown_seven_hundred_ninety_four: _Optional[str] = ...) -> None: ...
        class UnknownFourHundredSixtyEight(_message.Message):
            __slots__ = ("unknown_seven_hundred_ninety_five", "unknown_seven_hundred_ninety_six", "unknown_seven_hundred_ninety_seven")
            UNKNOWN_SEVEN_HUNDRED_NINETY_FIVE_FIELD_NUMBER: _ClassVar[int]
            UNKNOWN_SEVEN_HUNDRED_NINETY_SIX_FIELD_NUMBER: _ClassVar[int]
            UNKNOWN_SEVEN_HUNDRED_NINETY_SEVEN_FIELD_NUMBER: _ClassVar[int]
            unknown_seven_hundred_ninety_five: str
            unknown_seven_hundred_ninety_six: str
            unknown_seven_hundred_ninety_seven: _common_pb2.SocialEmblem
            def __init__(self, unknown_seven_hundred_ninety_five: _Optional[str] = ..., unknown_seven_hundred_ninety_six: _Optional[str] = ..., unknown_seven_hundred_ninety_seven: _Optional[_Union[_common_pb2.SocialEmblem, _Mapping]] = ...) -> None: ...
        class UnknownFourHundredSixtyNine(_message.Message):
            __slots__ = ("unknown_seven_hundred_ninety_eight",)
            UNKNOWN_SEVEN_HUNDRED_NINETY_EIGHT_FIELD_NUMBER: _ClassVar[int]
            unknown_seven_hundred_ninety_eight: _common_pb2.MapExtendedCoordinates
            def __init__(self, unknown_seven_hundred_ninety_eight: _Optional[_Union[_common_pb2.MapExtendedCoordinates, _Mapping]] = ...) -> None: ...
        UNKNOWN_SEVEN_HUNDRED_NINETY_NINE_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_EIGHT_HUNDRED_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_EIGHT_HUNDRED_ONE_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_EIGHT_HUNDRED_TWO_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_EIGHT_HUNDRED_THREE_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_EIGHT_HUNDRED_FOUR_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_EIGHT_HUNDRED_FIVE_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_EIGHT_HUNDRED_SIX_FIELD_NUMBER: _ClassVar[int]
        unknown_seven_hundred_ninety_nine: _common_pb2.UnknownOneHundredTwenty
        unknown_eight_hundred: UnknownFourHundredSixty.UnknownFourHundredSixtyFive.UnknownFourHundredSixtySeven
        unknown_eight_hundred_one: _containers.ScalarMap[int, int]
        unknown_eight_hundred_two: UnknownFourHundredSixty.UnknownFourHundredSixtyFive.UnknownFourHundredSixtySix
        unknown_eight_hundred_three: _containers.RepeatedScalarFieldContainer[int]
        unknown_eight_hundred_four: UnknownFourHundredSixty.UnknownFourHundredSixtyFive.UnknownFourHundredSixtyNine
        unknown_eight_hundred_five: UnknownFourHundredSixty.UnknownFourHundredSixtyFive.UnknownFourHundredSixtyEight
        unknown_eight_hundred_six: int
        def __init__(self, unknown_seven_hundred_ninety_nine: _Optional[_Union[_common_pb2.UnknownOneHundredTwenty, _Mapping]] = ..., unknown_eight_hundred: _Optional[_Union[UnknownFourHundredSixty.UnknownFourHundredSixtyFive.UnknownFourHundredSixtySeven, _Mapping]] = ..., unknown_eight_hundred_one: _Optional[_Mapping[int, int]] = ..., unknown_eight_hundred_two: _Optional[_Union[UnknownFourHundredSixty.UnknownFourHundredSixtyFive.UnknownFourHundredSixtySix, _Mapping]] = ..., unknown_eight_hundred_three: _Optional[_Iterable[int]] = ..., unknown_eight_hundred_four: _Optional[_Union[UnknownFourHundredSixty.UnknownFourHundredSixtyFive.UnknownFourHundredSixtyNine, _Mapping]] = ..., unknown_eight_hundred_five: _Optional[_Union[UnknownFourHundredSixty.UnknownFourHundredSixtyFive.UnknownFourHundredSixtyEight, _Mapping]] = ..., unknown_eight_hundred_six: _Optional[int] = ...) -> None: ...
    class UnknownFourHundredSeventy(_message.Message):
        __slots__ = ("unknown_eight_hundred_seven", "unknown_eight_hundred_eight", "unknown_eight_hundred_nine")
        class UnknownEightHundredSevenEntry(_message.Message):
            __slots__ = ("key", "value")
            KEY_FIELD_NUMBER: _ClassVar[int]
            VALUE_FIELD_NUMBER: _ClassVar[int]
            key: int
            value: int
            def __init__(self, key: _Optional[int] = ..., value: _Optional[int] = ...) -> None: ...
        class UnknownEightHundredEightEntry(_message.Message):
            __slots__ = ("key", "value")
            KEY_FIELD_NUMBER: _ClassVar[int]
            VALUE_FIELD_NUMBER: _ClassVar[int]
            key: int
            value: int
            def __init__(self, key: _Optional[int] = ..., value: _Optional[int] = ...) -> None: ...
        UNKNOWN_EIGHT_HUNDRED_SEVEN_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_EIGHT_HUNDRED_EIGHT_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_EIGHT_HUNDRED_NINE_FIELD_NUMBER: _ClassVar[int]
        unknown_eight_hundred_seven: _containers.ScalarMap[int, int]
        unknown_eight_hundred_eight: _containers.ScalarMap[int, int]
        unknown_eight_hundred_nine: _preset_pb2.CharacteristicsInfo
        def __init__(self, unknown_eight_hundred_seven: _Optional[_Mapping[int, int]] = ..., unknown_eight_hundred_eight: _Optional[_Mapping[int, int]] = ..., unknown_eight_hundred_nine: _Optional[_Union[_preset_pb2.CharacteristicsInfo, _Mapping]] = ...) -> None: ...
    class UnknownFourHundredSeventyOne(_message.Message):
        __slots__ = ("unknown_eight_hundred_twenty_three",)
        class UnknownFourHundredSeventyTwo(_message.Message):
            __slots__ = ("unknown_eight_hundred_nineteen", "unknown_eight_hundred_twenty", "unknown_eight_hundred_twenty_one", "unknown_eight_hundred_twenty_two")
            class UnknownFourHundredSeventyThree(_message.Message):
                __slots__ = ("unknown_eight_hundred_ten", "unknown_eight_hundred_eleven")
                UNKNOWN_EIGHT_HUNDRED_TEN_FIELD_NUMBER: _ClassVar[int]
                UNKNOWN_EIGHT_HUNDRED_ELEVEN_FIELD_NUMBER: _ClassVar[int]
                unknown_eight_hundred_ten: int
                unknown_eight_hundred_eleven: int
                def __init__(self, unknown_eight_hundred_ten: _Optional[int] = ..., unknown_eight_hundred_eleven: _Optional[int] = ...) -> None: ...
            class UnknownFourHundredSeventyFour(_message.Message):
                __slots__ = ("unknown_eight_hundred_twelve", "unknown_eight_hundred_thirteen")
                UNKNOWN_EIGHT_HUNDRED_TWELVE_FIELD_NUMBER: _ClassVar[int]
                UNKNOWN_EIGHT_HUNDRED_THIRTEEN_FIELD_NUMBER: _ClassVar[int]
                unknown_eight_hundred_twelve: int
                unknown_eight_hundred_thirteen: int
                def __init__(self, unknown_eight_hundred_twelve: _Optional[int] = ..., unknown_eight_hundred_thirteen: _Optional[int] = ...) -> None: ...
            class UnknownFourHundredSeventyFive(_message.Message):
                __slots__ = ("unknown_eight_hundred_fourteen", "unknown_eight_hundred_fifteen", "unknown_eight_hundred_sixteen", "unknown_eight_hundred_seventeen")
                UNKNOWN_EIGHT_HUNDRED_FOURTEEN_FIELD_NUMBER: _ClassVar[int]
                UNKNOWN_EIGHT_HUNDRED_FIFTEEN_FIELD_NUMBER: _ClassVar[int]
                UNKNOWN_EIGHT_HUNDRED_SIXTEEN_FIELD_NUMBER: _ClassVar[int]
                UNKNOWN_EIGHT_HUNDRED_SEVENTEEN_FIELD_NUMBER: _ClassVar[int]
                unknown_eight_hundred_fourteen: int
                unknown_eight_hundred_fifteen: int
                unknown_eight_hundred_sixteen: int
                unknown_eight_hundred_seventeen: int
                def __init__(self, unknown_eight_hundred_fourteen: _Optional[int] = ..., unknown_eight_hundred_fifteen: _Optional[int] = ..., unknown_eight_hundred_sixteen: _Optional[int] = ..., unknown_eight_hundred_seventeen: _Optional[int] = ...) -> None: ...
            class UnknownFourHundredSeventySix(_message.Message):
                __slots__ = ("unknown_eight_hundred_eighteen",)
                UNKNOWN_EIGHT_HUNDRED_EIGHTEEN_FIELD_NUMBER: _ClassVar[int]
                unknown_eight_hundred_eighteen: _containers.RepeatedScalarFieldContainer[int]
                def __init__(self, unknown_eight_hundred_eighteen: _Optional[_Iterable[int]] = ...) -> None: ...
            UNKNOWN_EIGHT_HUNDRED_NINETEEN_FIELD_NUMBER: _ClassVar[int]
            UNKNOWN_EIGHT_HUNDRED_TWENTY_FIELD_NUMBER: _ClassVar[int]
            UNKNOWN_EIGHT_HUNDRED_TWENTY_ONE_FIELD_NUMBER: _ClassVar[int]
            UNKNOWN_EIGHT_HUNDRED_TWENTY_TWO_FIELD_NUMBER: _ClassVar[int]
            unknown_eight_hundred_nineteen: UnknownFourHundredSixty.UnknownFourHundredSeventyOne.UnknownFourHundredSeventyTwo.UnknownFourHundredSeventyFive
            unknown_eight_hundred_twenty: UnknownFourHundredSixty.UnknownFourHundredSeventyOne.UnknownFourHundredSeventyTwo.UnknownFourHundredSeventyThree
            unknown_eight_hundred_twenty_one: UnknownFourHundredSixty.UnknownFourHundredSeventyOne.UnknownFourHundredSeventyTwo.UnknownFourHundredSeventySix
            unknown_eight_hundred_twenty_two: UnknownFourHundredSixty.UnknownFourHundredSeventyOne.UnknownFourHundredSeventyTwo.UnknownFourHundredSeventyFour
            def __init__(self, unknown_eight_hundred_nineteen: _Optional[_Union[UnknownFourHundredSixty.UnknownFourHundredSeventyOne.UnknownFourHundredSeventyTwo.UnknownFourHundredSeventyFive, _Mapping]] = ..., unknown_eight_hundred_twenty: _Optional[_Union[UnknownFourHundredSixty.UnknownFourHundredSeventyOne.UnknownFourHundredSeventyTwo.UnknownFourHundredSeventyThree, _Mapping]] = ..., unknown_eight_hundred_twenty_one: _Optional[_Union[UnknownFourHundredSixty.UnknownFourHundredSeventyOne.UnknownFourHundredSeventyTwo.UnknownFourHundredSeventySix, _Mapping]] = ..., unknown_eight_hundred_twenty_two: _Optional[_Union[UnknownFourHundredSixty.UnknownFourHundredSeventyOne.UnknownFourHundredSeventyTwo.UnknownFourHundredSeventyFour, _Mapping]] = ...) -> None: ...
        UNKNOWN_EIGHT_HUNDRED_TWENTY_THREE_FIELD_NUMBER: _ClassVar[int]
        unknown_eight_hundred_twenty_three: _containers.RepeatedCompositeFieldContainer[UnknownFourHundredSixty.UnknownFourHundredSeventyOne.UnknownFourHundredSeventyTwo]
        def __init__(self, unknown_eight_hundred_twenty_three: _Optional[_Iterable[_Union[UnknownFourHundredSixty.UnknownFourHundredSeventyOne.UnknownFourHundredSeventyTwo, _Mapping]]] = ...) -> None: ...
    UNKNOWN_EIGHT_HUNDRED_TWENTY_FOUR_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_EIGHT_HUNDRED_TWENTY_FIVE_FIELD_NUMBER: _ClassVar[int]
    unknown_eight_hundred_twenty_four: UnknownFourHundredSixty.UnknownFourHundredSixtyOne
    unknown_eight_hundred_twenty_five: UnknownFourHundredSixty.UnknownFourHundredSixtyThree
    def __init__(self, unknown_eight_hundred_twenty_four: _Optional[_Union[UnknownFourHundredSixty.UnknownFourHundredSixtyOne, _Mapping]] = ..., unknown_eight_hundred_twenty_five: _Optional[_Union[UnknownFourHundredSixty.UnknownFourHundredSixtyThree, _Mapping]] = ...) -> None: ...

class UnknownFourHundredSeventySeven(_message.Message):
    __slots__ = ("unknown_eight_hundred_twenty_six", "unknown_eight_hundred_twenty_seven")
    class UnknownFourHundredSeventyEight(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    UNKNOWN_EIGHT_HUNDRED_TWENTY_SIX_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_EIGHT_HUNDRED_TWENTY_SEVEN_FIELD_NUMBER: _ClassVar[int]
    unknown_eight_hundred_twenty_six: UnknownFourHundredSeventySeven.UnknownFourHundredSeventyEight
    unknown_eight_hundred_twenty_seven: UnknownFourHundredFortyFour
    def __init__(self, unknown_eight_hundred_twenty_six: _Optional[_Union[UnknownFourHundredSeventySeven.UnknownFourHundredSeventyEight, _Mapping]] = ..., unknown_eight_hundred_twenty_seven: _Optional[_Union[UnknownFourHundredFortyFour, _Mapping]] = ...) -> None: ...

class UnknownFourHundredSeventyNine(_message.Message):
    __slots__ = ("unknown_eight_hundred_twenty_eight", "unknown_eight_hundred_twenty_nine", "unknown_eight_hundred_thirty", "unknown_eight_hundred_thirty_one", "unknown_eight_hundred_thirty_two", "unknown_eight_hundred_thirty_three", "unknown_eight_hundred_thirty_four", "unknown_eight_hundred_thirty_five", "unknown_eight_hundred_thirty_six", "unknown_eight_hundred_thirty_seven", "unknown_eight_hundred_thirty_eight")
    class UnknownFourHundredEighty(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN_FOUR_HUNDRED_EIGHTY_UNSPECIFIED: _ClassVar[UnknownFourHundredSeventyNine.UnknownFourHundredEighty]
        UNKNOWN_FOUR_HUNDRED_EIGHTY_1: _ClassVar[UnknownFourHundredSeventyNine.UnknownFourHundredEighty]
    UNKNOWN_FOUR_HUNDRED_EIGHTY_UNSPECIFIED: UnknownFourHundredSeventyNine.UnknownFourHundredEighty
    UNKNOWN_FOUR_HUNDRED_EIGHTY_1: UnknownFourHundredSeventyNine.UnknownFourHundredEighty
    UNKNOWN_EIGHT_HUNDRED_TWENTY_EIGHT_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_EIGHT_HUNDRED_TWENTY_NINE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_EIGHT_HUNDRED_THIRTY_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_EIGHT_HUNDRED_THIRTY_ONE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_EIGHT_HUNDRED_THIRTY_TWO_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_EIGHT_HUNDRED_THIRTY_THREE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_EIGHT_HUNDRED_THIRTY_FOUR_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_EIGHT_HUNDRED_THIRTY_FIVE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_EIGHT_HUNDRED_THIRTY_SIX_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_EIGHT_HUNDRED_THIRTY_SEVEN_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_EIGHT_HUNDRED_THIRTY_EIGHT_FIELD_NUMBER: _ClassVar[int]
    unknown_eight_hundred_twenty_eight: int
    unknown_eight_hundred_twenty_nine: int
    unknown_eight_hundred_thirty: int
    unknown_eight_hundred_thirty_one: bool
    unknown_eight_hundred_thirty_two: int
    unknown_eight_hundred_thirty_three: _common_pb2.EntityLook
    unknown_eight_hundred_thirty_four: int
    unknown_eight_hundred_thirty_five: UnknownFourHundredSeventyNine.UnknownFourHundredEighty
    unknown_eight_hundred_thirty_six: str
    unknown_eight_hundred_thirty_seven: int
    unknown_eight_hundred_thirty_eight: _common_pb2.EntityLook
    def __init__(self, unknown_eight_hundred_twenty_eight: _Optional[int] = ..., unknown_eight_hundred_twenty_nine: _Optional[int] = ..., unknown_eight_hundred_thirty: _Optional[int] = ..., unknown_eight_hundred_thirty_one: bool = ..., unknown_eight_hundred_thirty_two: _Optional[int] = ..., unknown_eight_hundred_thirty_three: _Optional[_Union[_common_pb2.EntityLook, _Mapping]] = ..., unknown_eight_hundred_thirty_four: _Optional[int] = ..., unknown_eight_hundred_thirty_five: _Optional[_Union[UnknownFourHundredSeventyNine.UnknownFourHundredEighty, str]] = ..., unknown_eight_hundred_thirty_six: _Optional[str] = ..., unknown_eight_hundred_thirty_seven: _Optional[int] = ..., unknown_eight_hundred_thirty_eight: _Optional[_Union[_common_pb2.EntityLook, _Mapping]] = ...) -> None: ...

class PlayerInfoEvent(_message.Message):
    __slots__ = ("unknown_seven_hundred_seventy_nine", "unknown_seven_hundred_eighty")
    class UnknownFourHundredForty(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class UnknownFourHundredFortyOne(_message.Message):
        __slots__ = ("unknown_seven_hundred_seventy_eight",)
        class UnknownFourHundredFortyTwo(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            UNKNOWN_FOUR_HUNDRED_FORTY_TWO_UNSPECIFIED: _ClassVar[PlayerInfoEvent.UnknownFourHundredFortyOne.UnknownFourHundredFortyTwo]
            UNKNOWN_FOUR_HUNDRED_FORTY_TWO_1: _ClassVar[PlayerInfoEvent.UnknownFourHundredFortyOne.UnknownFourHundredFortyTwo]
            UNKNOWN_FOUR_HUNDRED_FORTY_TWO_2: _ClassVar[PlayerInfoEvent.UnknownFourHundredFortyOne.UnknownFourHundredFortyTwo]
        UNKNOWN_FOUR_HUNDRED_FORTY_TWO_UNSPECIFIED: PlayerInfoEvent.UnknownFourHundredFortyOne.UnknownFourHundredFortyTwo
        UNKNOWN_FOUR_HUNDRED_FORTY_TWO_1: PlayerInfoEvent.UnknownFourHundredFortyOne.UnknownFourHundredFortyTwo
        UNKNOWN_FOUR_HUNDRED_FORTY_TWO_2: PlayerInfoEvent.UnknownFourHundredFortyOne.UnknownFourHundredFortyTwo
        UNKNOWN_SEVEN_HUNDRED_SEVENTY_EIGHT_FIELD_NUMBER: _ClassVar[int]
        unknown_seven_hundred_seventy_eight: PlayerInfoEvent.UnknownFourHundredFortyOne.UnknownFourHundredFortyTwo
        def __init__(self, unknown_seven_hundred_seventy_eight: _Optional[_Union[PlayerInfoEvent.UnknownFourHundredFortyOne.UnknownFourHundredFortyTwo, str]] = ...) -> None: ...
    UNKNOWN_SEVEN_HUNDRED_SEVENTY_NINE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_SEVEN_HUNDRED_EIGHTY_FIELD_NUMBER: _ClassVar[int]
    unknown_seven_hundred_seventy_nine: PlayerInfoEvent.UnknownFourHundredFortyOne
    unknown_seven_hundred_eighty: PlayerInfoEvent.UnknownFourHundredForty
    def __init__(self, unknown_seven_hundred_seventy_nine: _Optional[_Union[PlayerInfoEvent.UnknownFourHundredFortyOne, _Mapping]] = ..., unknown_seven_hundred_eighty: _Optional[_Union[PlayerInfoEvent.UnknownFourHundredForty, _Mapping]] = ...) -> None: ...

class UnknownFourHundredEightyOne(_message.Message):
    __slots__ = ("unknown_eight_hundred_thirty_nine", "unknown_eight_hundred_forty")
    UNKNOWN_EIGHT_HUNDRED_THIRTY_NINE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_EIGHT_HUNDRED_FORTY_FIELD_NUMBER: _ClassVar[int]
    unknown_eight_hundred_thirty_nine: UnknownFourHundredFortyFive
    unknown_eight_hundred_forty: int
    def __init__(self, unknown_eight_hundred_thirty_nine: _Optional[_Union[UnknownFourHundredFortyFive, str]] = ..., unknown_eight_hundred_forty: _Optional[int] = ...) -> None: ...

class PlayerInfoRequest(_message.Message):
    __slots__ = ("unknown_seven_hundred_eighty_one",)
    UNKNOWN_SEVEN_HUNDRED_EIGHTY_ONE_FIELD_NUMBER: _ClassVar[int]
    unknown_seven_hundred_eighty_one: int
    def __init__(self, unknown_seven_hundred_eighty_one: _Optional[int] = ...) -> None: ...
