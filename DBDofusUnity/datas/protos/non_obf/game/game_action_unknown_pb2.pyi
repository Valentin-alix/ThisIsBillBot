from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class UnknownOneHundredEightyFour(_message.Message):
    __slots__ = ("unknown_three_hundred_eighty_six",)
    UNKNOWN_THREE_HUNDRED_EIGHTY_SIX_FIELD_NUMBER: _ClassVar[int]
    unknown_three_hundred_eighty_six: UnknownOneHundredEightySix
    def __init__(self, unknown_three_hundred_eighty_six: _Optional[_Union[UnknownOneHundredEightySix, _Mapping]] = ...) -> None: ...

class UnknownOneHundredEightyFive(_message.Message):
    __slots__ = ("unknown_three_hundred_eighty_seven", "unknown_three_hundred_eighty_eight")
    UNKNOWN_THREE_HUNDRED_EIGHTY_SEVEN_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_THREE_HUNDRED_EIGHTY_EIGHT_FIELD_NUMBER: _ClassVar[int]
    unknown_three_hundred_eighty_seven: _containers.RepeatedCompositeFieldContainer[UnknownOneHundredEightySix]
    unknown_three_hundred_eighty_eight: _containers.RepeatedCompositeFieldContainer[UnknownOneHundredEightySix]
    def __init__(self, unknown_three_hundred_eighty_seven: _Optional[_Iterable[_Union[UnknownOneHundredEightySix, _Mapping]]] = ..., unknown_three_hundred_eighty_eight: _Optional[_Iterable[_Union[UnknownOneHundredEightySix, _Mapping]]] = ...) -> None: ...

class UnknownOneHundredEightySix(_message.Message):
    __slots__ = ("unknown_three_hundred_ninety", "unknown_three_hundred_ninety_one", "unknown_three_hundred_ninety_two")
    class UnknownOneHundredEightySeven(_message.Message):
        __slots__ = ("unknown_three_hundred_eighty_nine",)
        UNKNOWN_THREE_HUNDRED_EIGHTY_NINE_FIELD_NUMBER: _ClassVar[int]
        unknown_three_hundred_eighty_nine: int
        def __init__(self, unknown_three_hundred_eighty_nine: _Optional[int] = ...) -> None: ...
    class UnknownOneHundredEightyEight(_message.Message):
        __slots__ = ()
        class UnknownOneHundredEightyNine(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            UNKNOWN_ONE_HUNDRED_EIGHTY_NINE_UNSPECIFIED: _ClassVar[UnknownOneHundredEightySix.UnknownOneHundredEightyEight.UnknownOneHundredEightyNine]
            UNKNOWN_ONE_HUNDRED_EIGHTY_NINE_1: _ClassVar[UnknownOneHundredEightySix.UnknownOneHundredEightyEight.UnknownOneHundredEightyNine]
        UNKNOWN_ONE_HUNDRED_EIGHTY_NINE_UNSPECIFIED: UnknownOneHundredEightySix.UnknownOneHundredEightyEight.UnknownOneHundredEightyNine
        UNKNOWN_ONE_HUNDRED_EIGHTY_NINE_1: UnknownOneHundredEightySix.UnknownOneHundredEightyEight.UnknownOneHundredEightyNine
        def __init__(self) -> None: ...
    UNKNOWN_THREE_HUNDRED_NINETY_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_THREE_HUNDRED_NINETY_ONE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_THREE_HUNDRED_NINETY_TWO_FIELD_NUMBER: _ClassVar[int]
    unknown_three_hundred_ninety: _containers.RepeatedCompositeFieldContainer[UnknownOneHundredEightySix.UnknownOneHundredEightyEight]
    unknown_three_hundred_ninety_one: int
    unknown_three_hundred_ninety_two: UnknownOneHundredEightySix.UnknownOneHundredEightySeven
    def __init__(self, unknown_three_hundred_ninety: _Optional[_Iterable[_Union[UnknownOneHundredEightySix.UnknownOneHundredEightyEight, _Mapping]]] = ..., unknown_three_hundred_ninety_one: _Optional[int] = ..., unknown_three_hundred_ninety_two: _Optional[_Union[UnknownOneHundredEightySix.UnknownOneHundredEightySeven, _Mapping]] = ...) -> None: ...

class UnknownOneHundredNinety(_message.Message):
    __slots__ = ("unknown_three_hundred_ninety_three", "unknown_three_hundred_ninety_four")
    UNKNOWN_THREE_HUNDRED_NINETY_THREE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_THREE_HUNDRED_NINETY_FOUR_FIELD_NUMBER: _ClassVar[int]
    unknown_three_hundred_ninety_three: bool
    unknown_three_hundred_ninety_four: str
    def __init__(self, unknown_three_hundred_ninety_three: bool = ..., unknown_three_hundred_ninety_four: _Optional[str] = ...) -> None: ...

class UnknownOneHundredNinetyOne(_message.Message):
    __slots__ = ("unknown_three_hundred_ninety_five",)
    UNKNOWN_THREE_HUNDRED_NINETY_FIVE_FIELD_NUMBER: _ClassVar[int]
    unknown_three_hundred_ninety_five: UnknownOneHundredEightyFive
    def __init__(self, unknown_three_hundred_ninety_five: _Optional[_Union[UnknownOneHundredEightyFive, _Mapping]] = ...) -> None: ...

class UnknownOneHundredNinetyTwo(_message.Message):
    __slots__ = ("unknown_three_hundred_ninety_six",)
    UNKNOWN_THREE_HUNDRED_NINETY_SIX_FIELD_NUMBER: _ClassVar[int]
    unknown_three_hundred_ninety_six: int
    def __init__(self, unknown_three_hundred_ninety_six: _Optional[int] = ...) -> None: ...

class UnknownOneHundredNinetyThree(_message.Message):
    __slots__ = ("unknown_three_hundred_ninety_seven",)
    UNKNOWN_THREE_HUNDRED_NINETY_SEVEN_FIELD_NUMBER: _ClassVar[int]
    unknown_three_hundred_ninety_seven: str
    def __init__(self, unknown_three_hundred_ninety_seven: _Optional[str] = ...) -> None: ...

class GuildMissionConfigurationEvent(_message.Message):
    __slots__ = ("details", "unavailable")
    class GuildMissionConfigurationDetails(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class GuildMissionConfigurationUnavailable(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    DETAILS_FIELD_NUMBER: _ClassVar[int]
    UNAVAILABLE_FIELD_NUMBER: _ClassVar[int]
    details: GuildMissionConfigurationEvent.GuildMissionConfigurationDetails
    unavailable: GuildMissionConfigurationEvent.GuildMissionConfigurationUnavailable
    def __init__(self, details: _Optional[_Union[GuildMissionConfigurationEvent.GuildMissionConfigurationDetails, _Mapping]] = ..., unavailable: _Optional[_Union[GuildMissionConfigurationEvent.GuildMissionConfigurationUnavailable, _Mapping]] = ...) -> None: ...

class GuildMissionConfigurationRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GuildMissionSelectionSaveEvent(_message.Message):
    __slots__ = ("failure", "success")
    class GuildMissionSelectionSaveFailure(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class GuildMissionSelectionSaveSuccess(_message.Message):
        __slots__ = ("selected_missions",)
        SELECTED_MISSIONS_FIELD_NUMBER: _ClassVar[int]
        selected_missions: GuildMissionSelectionSaveRequest.GuildMissionSelection
        def __init__(self, selected_missions: _Optional[_Union[GuildMissionSelectionSaveRequest.GuildMissionSelection, _Mapping]] = ...) -> None: ...
    FAILURE_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    failure: GuildMissionSelectionSaveEvent.GuildMissionSelectionSaveFailure
    success: GuildMissionSelectionSaveEvent.GuildMissionSelectionSaveSuccess
    def __init__(self, failure: _Optional[_Union[GuildMissionSelectionSaveEvent.GuildMissionSelectionSaveFailure, _Mapping]] = ..., success: _Optional[_Union[GuildMissionSelectionSaveEvent.GuildMissionSelectionSaveSuccess, _Mapping]] = ...) -> None: ...

class GuildMissionSelectionSaveRequest(_message.Message):
    __slots__ = ("tier_id", "selected_missions")
    class GuildMissionSelection(_message.Message):
        __slots__ = ("mission_ids", "unknown_three_hundred_eighty_five")
        MISSION_IDS_FIELD_NUMBER: _ClassVar[int]
        UNKNOWN_THREE_HUNDRED_EIGHTY_FIVE_FIELD_NUMBER: _ClassVar[int]
        mission_ids: _containers.RepeatedScalarFieldContainer[int]
        unknown_three_hundred_eighty_five: _containers.RepeatedScalarFieldContainer[int]
        def __init__(self, mission_ids: _Optional[_Iterable[int]] = ..., unknown_three_hundred_eighty_five: _Optional[_Iterable[int]] = ...) -> None: ...
    TIER_ID_FIELD_NUMBER: _ClassVar[int]
    SELECTED_MISSIONS_FIELD_NUMBER: _ClassVar[int]
    tier_id: int
    selected_missions: GuildMissionSelectionSaveRequest.GuildMissionSelection
    def __init__(self, tier_id: _Optional[int] = ..., selected_missions: _Optional[_Union[GuildMissionSelectionSaveRequest.GuildMissionSelection, _Mapping]] = ...) -> None: ...
