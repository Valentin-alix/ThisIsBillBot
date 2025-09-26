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

class CharacterAppearanceCollectionEvent(_message.Message):
    __slots__ = ("character_faces", "character_colors")
    CHARACTER_FACES_FIELD_NUMBER: _ClassVar[int]
    CHARACTER_COLORS_FIELD_NUMBER: _ClassVar[int]
    character_faces: CharacterFaces
    character_colors: CharacterColors
    def __init__(self, character_faces: _Optional[_Union[CharacterFaces, _Mapping]] = ..., character_colors: _Optional[_Union[CharacterColors, _Mapping]] = ...) -> None: ...

class CharacterFaces(_message.Message):
    __slots__ = ("slots", "faces", "max_slots")
    SLOTS_FIELD_NUMBER: _ClassVar[int]
    FACES_FIELD_NUMBER: _ClassVar[int]
    MAX_SLOTS_FIELD_NUMBER: _ClassVar[int]
    slots: int
    faces: _containers.RepeatedScalarFieldContainer[int]
    max_slots: int
    def __init__(self, slots: _Optional[int] = ..., faces: _Optional[_Iterable[int]] = ..., max_slots: _Optional[int] = ...) -> None: ...

class CharacterColors(_message.Message):
    __slots__ = ("slots", "color_palettes", "max_slots")
    SLOTS_FIELD_NUMBER: _ClassVar[int]
    COLOR_PALETTES_FIELD_NUMBER: _ClassVar[int]
    MAX_SLOTS_FIELD_NUMBER: _ClassVar[int]
    slots: int
    color_palettes: _containers.RepeatedCompositeFieldContainer[ColorPalette]
    max_slots: int
    def __init__(self, slots: _Optional[int] = ..., color_palettes: _Optional[_Iterable[_Union[ColorPalette, _Mapping]]] = ..., max_slots: _Optional[int] = ...) -> None: ...

class ColorPalette(_message.Message):
    __slots__ = ("colors",)
    COLORS_FIELD_NUMBER: _ClassVar[int]
    colors: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, colors: _Optional[_Iterable[int]] = ...) -> None: ...

class CharacterUpdateColorsRequest(_message.Message):
    __slots__ = ("colors", "slot")
    COLORS_FIELD_NUMBER: _ClassVar[int]
    SLOT_FIELD_NUMBER: _ClassVar[int]
    colors: _containers.RepeatedScalarFieldContainer[int]
    slot: int
    def __init__(self, colors: _Optional[_Iterable[int]] = ..., slot: _Optional[int] = ...) -> None: ...

class CharacterColorsUpdatedEvent(_message.Message):
    __slots__ = ("colors", "slot")
    COLORS_FIELD_NUMBER: _ClassVar[int]
    SLOT_FIELD_NUMBER: _ClassVar[int]
    colors: _containers.RepeatedScalarFieldContainer[int]
    slot: int
    def __init__(self, colors: _Optional[_Iterable[int]] = ..., slot: _Optional[int] = ...) -> None: ...

class UnknownOneHundredThirtySeven(_message.Message):
    __slots__ = ("unknown_two_hundred_ninety_three", "unknown_two_hundred_ninety_four")
    UNKNOWN_TWO_HUNDRED_NINETY_THREE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_TWO_HUNDRED_NINETY_FOUR_FIELD_NUMBER: _ClassVar[int]
    unknown_two_hundred_ninety_three: int
    unknown_two_hundred_ninety_four: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, unknown_two_hundred_ninety_three: _Optional[int] = ..., unknown_two_hundred_ninety_four: _Optional[_Iterable[int]] = ...) -> None: ...

class UnknownOneHundredThirtyEight(_message.Message):
    __slots__ = ("unknown_two_hundred_ninety_five", "unknown_two_hundred_ninety_six", "unknown_two_hundred_ninety_seven", "unknown_two_hundred_ninety_eight", "unknown_two_hundred_ninety_nine")
    class UnknownOneHundredThirtyNine(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN_ONE_HUNDRED_THIRTY_NINE_UNSPECIFIED: _ClassVar[UnknownOneHundredThirtyEight.UnknownOneHundredThirtyNine]
    UNKNOWN_ONE_HUNDRED_THIRTY_NINE_UNSPECIFIED: UnknownOneHundredThirtyEight.UnknownOneHundredThirtyNine
    UNKNOWN_TWO_HUNDRED_NINETY_FIVE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_TWO_HUNDRED_NINETY_SIX_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_TWO_HUNDRED_NINETY_SEVEN_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_TWO_HUNDRED_NINETY_EIGHT_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_TWO_HUNDRED_NINETY_NINE_FIELD_NUMBER: _ClassVar[int]
    unknown_two_hundred_ninety_five: int
    unknown_two_hundred_ninety_six: _containers.RepeatedScalarFieldContainer[int]
    unknown_two_hundred_ninety_seven: str
    unknown_two_hundred_ninety_eight: UnknownOneHundredThirtyEight.UnknownOneHundredThirtyNine
    unknown_two_hundred_ninety_nine: int
    def __init__(self, unknown_two_hundred_ninety_five: _Optional[int] = ..., unknown_two_hundred_ninety_six: _Optional[_Iterable[int]] = ..., unknown_two_hundred_ninety_seven: _Optional[str] = ..., unknown_two_hundred_ninety_eight: _Optional[_Union[UnknownOneHundredThirtyEight.UnknownOneHundredThirtyNine, str]] = ..., unknown_two_hundred_ninety_nine: _Optional[int] = ...) -> None: ...

class UnknownOneHundredForty(_message.Message):
    __slots__ = ("unknown_three_hundred", "unknown_three_hundred_one", "unknown_three_hundred_two")
    class UnknownOneHundredFortyOne(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN_ONE_HUNDRED_FORTY_ONE_UNSPECIFIED: _ClassVar[UnknownOneHundredForty.UnknownOneHundredFortyOne]
    UNKNOWN_ONE_HUNDRED_FORTY_ONE_UNSPECIFIED: UnknownOneHundredForty.UnknownOneHundredFortyOne
    UNKNOWN_THREE_HUNDRED_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_THREE_HUNDRED_ONE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_THREE_HUNDRED_TWO_FIELD_NUMBER: _ClassVar[int]
    unknown_three_hundred: UnknownOneHundredForty.UnknownOneHundredFortyOne
    unknown_three_hundred_one: _common_pb2.EntityLook
    unknown_three_hundred_two: str
    def __init__(self, unknown_three_hundred: _Optional[_Union[UnknownOneHundredForty.UnknownOneHundredFortyOne, str]] = ..., unknown_three_hundred_one: _Optional[_Union[_common_pb2.EntityLook, _Mapping]] = ..., unknown_three_hundred_two: _Optional[str] = ...) -> None: ...

class UnknownOneHundredFortyTwo(_message.Message):
    __slots__ = ("unknown_three_hundred_three", "unknown_three_hundred_four")
    class UnknownOneHundredFortyThree(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN_ONE_HUNDRED_FORTY_THREE_UNSPECIFIED: _ClassVar[UnknownOneHundredFortyTwo.UnknownOneHundredFortyThree]
    UNKNOWN_ONE_HUNDRED_FORTY_THREE_UNSPECIFIED: UnknownOneHundredFortyTwo.UnknownOneHundredFortyThree
    UNKNOWN_THREE_HUNDRED_THREE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_THREE_HUNDRED_FOUR_FIELD_NUMBER: _ClassVar[int]
    unknown_three_hundred_three: UnknownOneHundredFortyTwo.UnknownOneHundredFortyThree
    unknown_three_hundred_four: str
    def __init__(self, unknown_three_hundred_three: _Optional[_Union[UnknownOneHundredFortyTwo.UnknownOneHundredFortyThree, str]] = ..., unknown_three_hundred_four: _Optional[str] = ...) -> None: ...

class UnknownOneHundredFortyFour(_message.Message):
    __slots__ = ("unknown_three_hundred_five", "unknown_three_hundred_six", "unknown_three_hundred_seven", "unknown_three_hundred_eight", "unknown_three_hundred_nine", "unknown_three_hundred_ten")
    class UnknownOneHundredFortyFive(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN_ONE_HUNDRED_FORTY_FIVE_UNSPECIFIED: _ClassVar[UnknownOneHundredFortyFour.UnknownOneHundredFortyFive]
    UNKNOWN_ONE_HUNDRED_FORTY_FIVE_UNSPECIFIED: UnknownOneHundredFortyFour.UnknownOneHundredFortyFive
    UNKNOWN_THREE_HUNDRED_FIVE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_THREE_HUNDRED_SIX_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_THREE_HUNDRED_SEVEN_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_THREE_HUNDRED_EIGHT_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_THREE_HUNDRED_NINE_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_THREE_HUNDRED_TEN_FIELD_NUMBER: _ClassVar[int]
    unknown_three_hundred_five: int
    unknown_three_hundred_six: int
    unknown_three_hundred_seven: UnknownOneHundredFortyFour.UnknownOneHundredFortyFive
    unknown_three_hundred_eight: int
    unknown_three_hundred_nine: str
    unknown_three_hundred_ten: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, unknown_three_hundred_five: _Optional[int] = ..., unknown_three_hundred_six: _Optional[int] = ..., unknown_three_hundred_seven: _Optional[_Union[UnknownOneHundredFortyFour.UnknownOneHundredFortyFive, str]] = ..., unknown_three_hundred_eight: _Optional[int] = ..., unknown_three_hundred_nine: _Optional[str] = ..., unknown_three_hundred_ten: _Optional[_Iterable[int]] = ...) -> None: ...

class AccessoryPreviewRequest(_message.Message):
    __slots__ = ("object_gid", "show_current_objects")
    OBJECT_GID_FIELD_NUMBER: _ClassVar[int]
    SHOW_CURRENT_OBJECTS_FIELD_NUMBER: _ClassVar[int]
    object_gid: _containers.RepeatedScalarFieldContainer[int]
    show_current_objects: bool
    def __init__(self, object_gid: _Optional[_Iterable[int]] = ..., show_current_objects: bool = ...) -> None: ...

class AccessoryPreviewEvent(_message.Message):
    __slots__ = ("look",)
    LOOK_FIELD_NUMBER: _ClassVar[int]
    look: _common_pb2.EntityLook
    def __init__(self, look: _Optional[_Union[_common_pb2.EntityLook, _Mapping]] = ...) -> None: ...
