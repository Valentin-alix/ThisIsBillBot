import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class UnknownNineteen(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN_NINETEEN: _ClassVar[UnknownNineteen]
UNKNOWN_NINETEEN: UnknownNineteen

class UnknownEighteen(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class UnknownTwenty(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class BreachEnterInstanceRequest(_message.Message):
    __slots__ = ("unknown_thirty_five", "unknown_thirty_six")
    class BreachInstanceInformation(_message.Message):
        __slots__ = ("instance_number",)
        INSTANCE_NUMBER_FIELD_NUMBER: _ClassVar[int]
        instance_number: int
        def __init__(self, instance_number: _Optional[int] = ...) -> None: ...
    class UnknownTen(_message.Message):
        __slots__ = ("unknown_thirty_two", "unknown_thirty_three", "unknown_thirty_four")
        UNKNOWN_THIRTY_TWO_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_THIRTY_THREE_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_THIRTY_FOUR_FIELD_NUMBER: _ClassVar[int]
        unknown_thirty_two: str
        unknown_thirty_three: int
        unknown_thirty_four: int
        def __init__(self, unknown_thirty_two: _Optional[str] = ..., unknown_thirty_three: _Optional[int] = ..., unknown_thirty_four: _Optional[int] = ...) -> None: ...
    UNKNOWN_THIRTY_FIVE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_THIRTY_SIX_FIELD_NUMBER: _ClassVar[int]
    unknown_thirty_five: BreachEnterInstanceRequest.UnknownTen
    unknown_thirty_six: BreachEnterInstanceRequest.BreachInstanceInformation
    def __init__(self, unknown_thirty_five: _Optional[_Union[BreachEnterInstanceRequest.UnknownTen, _Mapping]] = ..., unknown_thirty_six: _Optional[_Union[BreachEnterInstanceRequest.BreachInstanceInformation, _Mapping]] = ...) -> None: ...

class BreachPlayerInformation(_message.Message):
    __slots__ = ("player_name", "player_id", "breed_id", "gender")
    class UnknownSeventeen(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    PLAYER_NAME_FIELD_NUMBER: _ClassVar[int]
    PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
    BREED_ID_FIELD_NUMBER: _ClassVar[int]
    GENDER_FIELD_NUMBER: _ClassVar[int]
    player_name: str
    player_id: int
    breed_id: int
    gender: _common_pb2.Gender
    def __init__(self, player_name: _Optional[str] = ..., player_id: _Optional[int] = ..., breed_id: _Optional[int] = ..., gender: _Optional[_Union[_common_pb2.Gender, str]] = ...) -> None: ...

class UnknownTwentyTwo(_message.Message):
    __slots__ = ("unknown_eighty_six",)
    UNKNOWN_EIGHTY_SIX_FIELD_NUMBER: _ClassVar[int]
    unknown_eighty_six: str
    def __init__(self, unknown_eighty_six: _Optional[str] = ...) -> None: ...

class UnknownTwentyThree(_message.Message):
    __slots__ = ("unknown_eighty_eight", "unknown_eighty_nine", "unknown_ninety", "unknown_ninety_four", "unknown_ninety_one", "unknown_ninety_two", "unknown_ninety_three", "unknown_ninety_five", "unknown_ninety_six", "unknown_ninety_seven", "unknown_ninety_eight", "unknown_ninety_nine", "unknown_one_hundred", "unknown_one_hundred_one", "unknown_one_hundred_two")
    class UnknownTwentyFour(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class UnknownTwentyFive(_message.Message):
        __slots__ = ("unknown_eighty_seven",)
        UNKNOWN_EIGHTY_SEVEN_FIELD_NUMBER: _ClassVar[int]
        unknown_eighty_seven: int
        def __init__(self, unknown_eighty_seven: _Optional[int] = ...) -> None: ...
    class UnknownTwentySix(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    UNKNOWN_EIGHTY_EIGHT_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_EIGHTY_NINE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_NINETY_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_NINETY_FOUR_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_NINETY_ONE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_NINETY_TWO_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_NINETY_THREE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_NINETY_FIVE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_NINETY_SIX_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_NINETY_SEVEN_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_NINETY_EIGHT_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_NINETY_NINE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_ONE_HUNDRED_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_ONE_HUNDRED_ONE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_ONE_HUNDRED_TWO_FIELD_NUMBER: _ClassVar[int]
    unknown_eighty_eight: int
    unknown_eighty_nine: int
    unknown_ninety: int
    unknown_ninety_four: int
    unknown_ninety_one: str
    unknown_ninety_two: _containers.RepeatedCompositeFieldContainer[UnknownTwentySeven]
    unknown_ninety_three: _containers.RepeatedCompositeFieldContainer[UnknownTwentyEight]
    unknown_ninety_five: int
    unknown_ninety_six: int
    unknown_ninety_seven: int
    unknown_ninety_eight: int
    unknown_ninety_nine: int
    unknown_one_hundred: BreachPlayerInformation
    unknown_one_hundred_one: UnknownTwentyThree.UnknownTwentyFour
    unknown_one_hundred_two: UnknownTwentyThree.UnknownTwentyFive
    def __init__(self, unknown_eighty_eight: _Optional[int] = ..., unknown_eighty_nine: _Optional[int] = ..., unknown_ninety: _Optional[int] = ..., unknown_ninety_four: _Optional[int] = ..., unknown_ninety_one: _Optional[str] = ..., unknown_ninety_two: _Optional[_Iterable[_Union[UnknownTwentySeven, _Mapping]]] = ..., unknown_ninety_three: _Optional[_Iterable[_Union[UnknownTwentyEight, _Mapping]]] = ..., unknown_ninety_five: _Optional[int] = ..., unknown_ninety_six: _Optional[int] = ..., unknown_ninety_seven: _Optional[int] = ..., unknown_ninety_eight: _Optional[int] = ..., unknown_ninety_nine: _Optional[int] = ..., unknown_one_hundred: _Optional[_Union[BreachPlayerInformation, _Mapping]] = ..., unknown_one_hundred_one: _Optional[_Union[UnknownTwentyThree.UnknownTwentyFour, _Mapping]] = ..., unknown_one_hundred_two: _Optional[_Union[UnknownTwentyThree.UnknownTwentyFive, _Mapping]] = ...) -> None: ...

class UnknownTwentySeven(_message.Message):
    __slots__ = ("unknown_one_hundred_three", "unknown_one_hundred_four", "unknown_one_hundred_five", "unknown_one_hundred_six")
    class UnknownOneHundredThreeEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: UnknownEighteen
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[UnknownEighteen, _Mapping]] = ...) -> None: ...
    class UnknownOneHundredSixEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: UnknownTwenty
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[UnknownTwenty, _Mapping]] = ...) -> None: ...
    UNKNOWN_ONE_HUNDRED_THREE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_ONE_HUNDRED_FOUR_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_ONE_HUNDRED_FIVE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_ONE_HUNDRED_SIX_FIELD_NUMBER: _ClassVar[int]
    unknown_one_hundred_three: _containers.MessageMap[str, UnknownEighteen]
    unknown_one_hundred_four: UnknownNineteen
    unknown_one_hundred_five: _containers.RepeatedScalarFieldContainer[str]
    unknown_one_hundred_six: _containers.MessageMap[str, UnknownTwenty]
    def __init__(self, unknown_one_hundred_three: _Optional[_Mapping[str, UnknownEighteen]] = ..., unknown_one_hundred_four: _Optional[_Union[UnknownNineteen, str]] = ..., unknown_one_hundred_five: _Optional[_Iterable[str]] = ..., unknown_one_hundred_six: _Optional[_Mapping[str, UnknownTwenty]] = ...) -> None: ...

class UnknownTwentyEight(_message.Message):
    __slots__ = ("unknown_one_hundred_seven", "unknown_one_hundred_eight", "unknown_one_hundred_nine")
    UNKNOWN_ONE_HUNDRED_SEVEN_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_ONE_HUNDRED_EIGHT_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_ONE_HUNDRED_NINE_FIELD_NUMBER: _ClassVar[int]
    unknown_one_hundred_seven: _common_pb2.ObjectEffect
    unknown_one_hundred_eight: int
    unknown_one_hundred_nine: int
    def __init__(self, unknown_one_hundred_seven: _Optional[_Union[_common_pb2.ObjectEffect, _Mapping]] = ..., unknown_one_hundred_eight: _Optional[int] = ..., unknown_one_hundred_nine: _Optional[int] = ...) -> None: ...

class BreachCurrentInformationEvent(_message.Message):
    __slots__ = ("unknown_thirty_one",)
    class UnknownNine(_message.Message):
        __slots__ = ("unknown_seventeen", "unknown_eighteen", "unknown_nineteen", "unknown_twenty", "unknown_twenty_one", "unknown_twenty_two", "unknown_twenty_three", "unknown_twenty_four", "unknown_twenty_five", "unknown_twenty_six", "unknown_twenty_seven", "unknown_twenty_eight", "unknown_twenty_nine", "unknown_thirty")
        UNKNOWN_SEVENTEEN_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_EIGHTEEN_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_NINETEEN_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_TWENTY_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_TWENTY_ONE_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_TWENTY_TWO_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_TWENTY_THREE_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_TWENTY_FOUR_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_TWENTY_FIVE_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_TWENTY_SIX_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_TWENTY_SEVEN_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_TWENTY_EIGHT_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_TWENTY_NINE_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_THIRTY_FIELD_NUMBER: _ClassVar[int]
        unknown_seventeen: int
        unknown_eighteen: int
        unknown_nineteen: str
        unknown_twenty: int
        unknown_twenty_one: str
        unknown_twenty_two: _containers.RepeatedCompositeFieldContainer[UnknownTwentyEight]
        unknown_twenty_three: int
        unknown_twenty_four: int
        unknown_twenty_five: bool
        unknown_twenty_six: int
        unknown_twenty_seven: bool
        unknown_twenty_eight: bool
        unknown_twenty_nine: str
        unknown_thirty: _containers.RepeatedCompositeFieldContainer[UnknownTwentySeven]
        def __init__(self, unknown_seventeen: _Optional[int] = ..., unknown_eighteen: _Optional[int] = ..., unknown_nineteen: _Optional[str] = ..., unknown_twenty: _Optional[int] = ..., unknown_twenty_one: _Optional[str] = ..., unknown_twenty_two: _Optional[_Iterable[_Union[UnknownTwentyEight, _Mapping]]] = ..., unknown_twenty_three: _Optional[int] = ..., unknown_twenty_four: _Optional[int] = ..., unknown_twenty_five: bool = ..., unknown_twenty_six: _Optional[int] = ..., unknown_twenty_seven: bool = ..., unknown_twenty_eight: bool = ..., unknown_twenty_nine: _Optional[str] = ..., unknown_thirty: _Optional[_Iterable[_Union[UnknownTwentySeven, _Mapping]]] = ...) -> None: ...
    UNKNOWN_THIRTY_ONE_FIELD_NUMBER: _ClassVar[int]
    unknown_thirty_one: BreachCurrentInformationEvent.UnknownNine
    def __init__(self, unknown_thirty_one: _Optional[_Union[BreachCurrentInformationEvent.UnknownNine, _Mapping]] = ...) -> None: ...

class UnknownTwentyNine(_message.Message):
    __slots__ = ("unknown_one_hundred_eighteen", "unknown_one_hundred_nineteen", "unknown_one_hundred_twenty", "unknown_one_hundred_twenty_one")
    class UnknownThirty(_message.Message):
        __slots__ = ("unknown_one_hundred_ten", "unknown_one_hundred_eleven", "unknown_one_hundred_twelve", "unknown_one_hundred_thirteen", "unknown_one_hundred_fourteen", "unknown_one_hundred_fifteen", "unknown_one_hundred_sixteen", "unknown_one_hundred_seventeen")
        class UnknownOneHundredTenEntry(_message.Message):
            __slots__ = ("key", "value")
            KEY_FIELD_NUMBER: _ClassVar[int]
            VALUE_FIELD_NUMBER: _ClassVar[int]
            key: int
            value: int
            def __init__(self, key: _Optional[int] = ..., value: _Optional[int] = ...) -> None: ...
        class UnknownOneHundredTwelveEntry(_message.Message):
            __slots__ = ("key", "value")
            KEY_FIELD_NUMBER: _ClassVar[int]
            VALUE_FIELD_NUMBER: _ClassVar[int]
            key: bool
            value: str
            def __init__(self, key: bool = ..., value: _Optional[str] = ...) -> None: ...
        UNKNOWN_ONE_HUNDRED_TEN_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_ONE_HUNDRED_ELEVEN_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_ONE_HUNDRED_TWELVE_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_ONE_HUNDRED_THIRTEEN_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_ONE_HUNDRED_FOURTEEN_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_ONE_HUNDRED_FIFTEEN_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_ONE_HUNDRED_SIXTEEN_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_ONE_HUNDRED_SEVENTEEN_FIELD_NUMBER: _ClassVar[int]
        unknown_one_hundred_ten: _containers.ScalarMap[int, int]
        unknown_one_hundred_eleven: _containers.RepeatedScalarFieldContainer[int]
        unknown_one_hundred_twelve: _containers.ScalarMap[bool, str]
        unknown_one_hundred_thirteen: _containers.RepeatedScalarFieldContainer[int]
        unknown_one_hundred_fourteen: _containers.RepeatedScalarFieldContainer[str]
        unknown_one_hundred_fifteen: _containers.RepeatedScalarFieldContainer[str]
        unknown_one_hundred_sixteen: str
        unknown_one_hundred_seventeen: bool
        def __init__(self, unknown_one_hundred_ten: _Optional[_Mapping[int, int]] = ..., unknown_one_hundred_eleven: _Optional[_Iterable[int]] = ..., unknown_one_hundred_twelve: _Optional[_Mapping[bool, str]] = ..., unknown_one_hundred_thirteen: _Optional[_Iterable[int]] = ..., unknown_one_hundred_fourteen: _Optional[_Iterable[str]] = ..., unknown_one_hundred_fifteen: _Optional[_Iterable[str]] = ..., unknown_one_hundred_sixteen: _Optional[str] = ..., unknown_one_hundred_seventeen: bool = ...) -> None: ...
    UNKNOWN_ONE_HUNDRED_EIGHTEEN_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_ONE_HUNDRED_NINETEEN_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_ONE_HUNDRED_TWENTY_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_ONE_HUNDRED_TWENTY_ONE_FIELD_NUMBER: _ClassVar[int]
    unknown_one_hundred_eighteen: str
    unknown_one_hundred_nineteen: int
    unknown_one_hundred_twenty: int
    unknown_one_hundred_twenty_one: float
    def __init__(self, unknown_one_hundred_eighteen: _Optional[str] = ..., unknown_one_hundred_nineteen: _Optional[int] = ..., unknown_one_hundred_twenty: _Optional[int] = ..., unknown_one_hundred_twenty_one: _Optional[float] = ...) -> None: ...

class BreachEnterRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class UnknownTwentyOne(_message.Message):
    __slots__ = ("unknown_seventy_seven", "unknown_seventy_eight", "unknown_seventy_nine", "unknown_eighty", "unknown_eighty_one", "unknown_eighty_two", "unknown_eighty_three", "unknown_eighty_four", "unknown_eighty_five")
    UNKNOWN_SEVENTY_SEVEN_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_SEVENTY_EIGHT_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_SEVENTY_NINE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_EIGHTY_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_EIGHTY_ONE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_EIGHTY_TWO_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_EIGHTY_THREE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_EIGHTY_FOUR_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_EIGHTY_FIVE_FIELD_NUMBER: _ClassVar[int]
    unknown_seventy_seven: int
    unknown_seventy_eight: int
    unknown_seventy_nine: _containers.RepeatedCompositeFieldContainer[UnknownTwentyEight]
    unknown_eighty: int
    unknown_eighty_one: int
    unknown_eighty_two: int
    unknown_eighty_three: int
    unknown_eighty_four: int
    unknown_eighty_five: bool
    def __init__(self, unknown_seventy_seven: _Optional[int] = ..., unknown_seventy_eight: _Optional[int] = ..., unknown_seventy_nine: _Optional[_Iterable[_Union[UnknownTwentyEight, _Mapping]]] = ..., unknown_eighty: _Optional[int] = ..., unknown_eighty_one: _Optional[int] = ..., unknown_eighty_two: _Optional[int] = ..., unknown_eighty_three: _Optional[int] = ..., unknown_eighty_four: _Optional[int] = ..., unknown_eighty_five: bool = ...) -> None: ...

class BreachEnterInstanceResponse(_message.Message):
    __slots__ = ("unknown_fifty_two", "unknown_fifty_three", "unknown_fifty_four", "unknown_fifty_five", "unknown_fifty_six", "unknown_fifty_seven", "unknown_fifty_eight", "unknown_fifty_nine", "unknown_sixty", "unknown_sixty_one", "unknown_sixty_two", "unknown_sixty_three", "unknown_sixty_four", "unknown_sixty_five", "unknown_sixty_six", "unknown_sixty_seven", "unknown_sixty_eight", "unknown_sixty_nine", "unknown_seventy", "unknown_seventy_one", "unknown_seventy_two", "unknown_seventy_three")
    class UnknownEleven(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN_ELEVEN_UNSPECIFIED: _ClassVar[BreachEnterInstanceResponse.UnknownEleven]
        UNKNOWN_ELEVEN_1: _ClassVar[BreachEnterInstanceResponse.UnknownEleven]
        UNKNOWN_ELEVEN_2: _ClassVar[BreachEnterInstanceResponse.UnknownEleven]
        UNKNOWN_ELEVEN_3: _ClassVar[BreachEnterInstanceResponse.UnknownEleven]
        UNKNOWN_ELEVEN_4: _ClassVar[BreachEnterInstanceResponse.UnknownEleven]
    UNKNOWN_ELEVEN_UNSPECIFIED: BreachEnterInstanceResponse.UnknownEleven
    UNKNOWN_ELEVEN_1: BreachEnterInstanceResponse.UnknownEleven
    UNKNOWN_ELEVEN_2: BreachEnterInstanceResponse.UnknownEleven
    UNKNOWN_ELEVEN_3: BreachEnterInstanceResponse.UnknownEleven
    UNKNOWN_ELEVEN_4: BreachEnterInstanceResponse.UnknownEleven
    class UnknownSixteen(_message.Message):
        __slots__ = ("unknown_forty_eight", "unknown_forty_nine", "unknown_fifty", "unknown_fifty_one")
        class UnknownFiftyOneEntry(_message.Message):
            __slots__ = ("key", "value")
            KEY_FIELD_NUMBER: _ClassVar[int]
            VALUE_FIELD_NUMBER: _ClassVar[int]
            key: int
            value: int
            def __init__(self, key: _Optional[int] = ..., value: _Optional[int] = ...) -> None: ...
        UNKNOWN_FORTY_EIGHT_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FORTY_NINE_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FIFTY_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FIFTY_ONE_FIELD_NUMBER: _ClassVar[int]
        unknown_forty_eight: int
        unknown_forty_nine: int
        unknown_fifty: int
        unknown_fifty_one: _containers.ScalarMap[int, int]
        def __init__(self, unknown_forty_eight: _Optional[int] = ..., unknown_forty_nine: _Optional[int] = ..., unknown_fifty: _Optional[int] = ..., unknown_fifty_one: _Optional[_Mapping[int, int]] = ...) -> None: ...
    class UnknownTwelve(_message.Message):
        __slots__ = ("unknown_forty_five", "unknown_forty_six", "unknown_forty_seven")
        class UnknownThirteen(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            UNKNOWN_THIRTEEN_UNSPECIFIED: _ClassVar[BreachEnterInstanceResponse.UnknownTwelve.UnknownThirteen]
        UNKNOWN_THIRTEEN_UNSPECIFIED: BreachEnterInstanceResponse.UnknownTwelve.UnknownThirteen
        class UnknownFourteen(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            UNKNOWN_FOURTEEN_UNSPECIFIED: _ClassVar[BreachEnterInstanceResponse.UnknownTwelve.UnknownFourteen]
        UNKNOWN_FOURTEEN_UNSPECIFIED: BreachEnterInstanceResponse.UnknownTwelve.UnknownFourteen
        class UnknownFifteen(_message.Message):
            __slots__ = ("unknown_thirty_seven", "unknown_thirty_eight", "unknown_thirty_nine", "unknown_forty", "unknown_forty_one", "unknown_forty_two", "unknown_forty_three", "unknown_forty_four")
            class UnknownThirtyNineEntry(_message.Message):
                __slots__ = ("key", "value")
                KEY_FIELD_NUMBER: _ClassVar[int]
                VALUE_FIELD_NUMBER: _ClassVar[int]
                key: int
                value: bool
                def __init__(self, key: _Optional[int] = ..., value: bool = ...) -> None: ...
            UNKNOWN_THIRTY_SEVEN_FIELD_NUMBER: _ClassVar[int]
            UNKNOWN_THIRTY_EIGHT_FIELD_NUMBER: _ClassVar[int]
            UNKNOWN_THIRTY_NINE_FIELD_NUMBER: _ClassVar[int]
            UNKNOWN_FORTY_FIELD_NUMBER: _ClassVar[int]
            UNKNOWN_FORTY_ONE_FIELD_NUMBER: _ClassVar[int]
            UNKNOWN_FORTY_TWO_FIELD_NUMBER: _ClassVar[int]
            UNKNOWN_FORTY_THREE_FIELD_NUMBER: _ClassVar[int]
            UNKNOWN_FORTY_FOUR_FIELD_NUMBER: _ClassVar[int]
            unknown_thirty_seven: int
            unknown_thirty_eight: _containers.RepeatedScalarFieldContainer[int]
            unknown_thirty_nine: _containers.ScalarMap[int, bool]
            unknown_forty: int
            unknown_forty_one: str
            unknown_forty_two: _containers.RepeatedScalarFieldContainer[int]
            unknown_forty_three: int
            unknown_forty_four: _containers.RepeatedScalarFieldContainer[int]
            def __init__(self, unknown_thirty_seven: _Optional[int] = ..., unknown_thirty_eight: _Optional[_Iterable[int]] = ..., unknown_thirty_nine: _Optional[_Mapping[int, bool]] = ..., unknown_forty: _Optional[int] = ..., unknown_forty_one: _Optional[str] = ..., unknown_forty_two: _Optional[_Iterable[int]] = ..., unknown_forty_three: _Optional[int] = ..., unknown_forty_four: _Optional[_Iterable[int]] = ...) -> None: ...
        UNKNOWN_FORTY_FIVE_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FORTY_SIX_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_FORTY_SEVEN_FIELD_NUMBER: _ClassVar[int]
        unknown_forty_five: str
        unknown_forty_six: BreachEnterInstanceResponse.UnknownTwelve.UnknownThirteen
        unknown_forty_seven: BreachEnterInstanceResponse.UnknownTwelve.UnknownFourteen
        def __init__(self, unknown_forty_five: _Optional[str] = ..., unknown_forty_six: _Optional[_Union[BreachEnterInstanceResponse.UnknownTwelve.UnknownThirteen, str]] = ..., unknown_forty_seven: _Optional[_Union[BreachEnterInstanceResponse.UnknownTwelve.UnknownFourteen, str]] = ...) -> None: ...
    UNKNOWN_FIFTY_TWO_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FIFTY_THREE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FIFTY_FOUR_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FIFTY_FIVE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FIFTY_SIX_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FIFTY_SEVEN_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FIFTY_EIGHT_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FIFTY_NINE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_SIXTY_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_SIXTY_ONE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_SIXTY_TWO_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_SIXTY_THREE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_SIXTY_FOUR_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_SIXTY_FIVE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_SIXTY_SIX_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_SIXTY_SEVEN_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_SIXTY_EIGHT_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_SIXTY_NINE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_SEVENTY_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_SEVENTY_ONE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_SEVENTY_TWO_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_SEVENTY_THREE_FIELD_NUMBER: _ClassVar[int]
    unknown_fifty_two: BreachPlayerInformation
    unknown_fifty_three: _containers.RepeatedCompositeFieldContainer[BreachEnterInstanceResponse.UnknownSixteen]
    unknown_fifty_four: _containers.RepeatedCompositeFieldContainer[BreachEnterInstanceResponse.UnknownTwelve]
    unknown_fifty_five: _containers.RepeatedCompositeFieldContainer[BreachPlayerInformation]
    unknown_fifty_six: _containers.RepeatedCompositeFieldContainer[UnknownTwentyOne]
    unknown_fifty_seven: int
    unknown_fifty_eight: int
    unknown_fifty_nine: str
    unknown_sixty: int
    unknown_sixty_one: int
    unknown_sixty_two: BreachEnterInstanceResponse.UnknownEleven
    unknown_sixty_three: str
    unknown_sixty_four: int
    unknown_sixty_five: _containers.RepeatedCompositeFieldContainer[UnknownTwentyEight]
    unknown_sixty_six: _containers.RepeatedCompositeFieldContainer[UnknownTwentySeven]
    unknown_sixty_seven: int
    unknown_sixty_eight: bool
    unknown_sixty_nine: bool
    unknown_seventy: int
    unknown_seventy_one: bool
    unknown_seventy_two: int
    unknown_seventy_three: bool
    def __init__(self, unknown_fifty_two: _Optional[_Union[BreachPlayerInformation, _Mapping]] = ..., unknown_fifty_three: _Optional[_Iterable[_Union[BreachEnterInstanceResponse.UnknownSixteen, _Mapping]]] = ..., unknown_fifty_four: _Optional[_Iterable[_Union[BreachEnterInstanceResponse.UnknownTwelve, _Mapping]]] = ..., unknown_fifty_five: _Optional[_Iterable[_Union[BreachPlayerInformation, _Mapping]]] = ..., unknown_fifty_six: _Optional[_Iterable[_Union[UnknownTwentyOne, _Mapping]]] = ..., unknown_fifty_seven: _Optional[int] = ..., unknown_fifty_eight: _Optional[int] = ..., unknown_fifty_nine: _Optional[str] = ..., unknown_sixty: _Optional[int] = ..., unknown_sixty_one: _Optional[int] = ..., unknown_sixty_two: _Optional[_Union[BreachEnterInstanceResponse.UnknownEleven, str]] = ..., unknown_sixty_three: _Optional[str] = ..., unknown_sixty_four: _Optional[int] = ..., unknown_sixty_five: _Optional[_Iterable[_Union[UnknownTwentyEight, _Mapping]]] = ..., unknown_sixty_six: _Optional[_Iterable[_Union[UnknownTwentySeven, _Mapping]]] = ..., unknown_sixty_seven: _Optional[int] = ..., unknown_sixty_eight: bool = ..., unknown_sixty_nine: bool = ..., unknown_seventy: _Optional[int] = ..., unknown_seventy_one: bool = ..., unknown_seventy_two: _Optional[int] = ..., unknown_seventy_three: bool = ...) -> None: ...

class BreachRoomLootEvent(_message.Message):
    __slots__ = ("unknown_seventy_five", "unknown_seventy_six")
    UNKNOWN_SEVENTY_FIVE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_SEVENTY_SIX_FIELD_NUMBER: _ClassVar[int]
    unknown_seventy_five: bool
    unknown_seventy_six: _containers.RepeatedCompositeFieldContainer[UnknownTwentyNine]
    def __init__(self, unknown_seventy_five: bool = ..., unknown_seventy_six: _Optional[_Iterable[_Union[UnknownTwentyNine, _Mapping]]] = ...) -> None: ...

class BreachRoomLootRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class BreachExitRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class BreachRerollMonstersRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class BreachExitEvent(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class BreachExitResultEvent(_message.Message):
    __slots__ = ("exited",)
    EXITED_FIELD_NUMBER: _ClassVar[int]
    exited: bool
    def __init__(self, exited: bool = ...) -> None: ...

class BreachRerollMonstersResponse(_message.Message):
    __slots__ = ("unknown_seventy_four",)
    UNKNOWN_SEVENTY_FOUR_FIELD_NUMBER: _ClassVar[int]
    unknown_seventy_four: bool
    def __init__(self, unknown_seventy_four: bool = ...) -> None: ...
