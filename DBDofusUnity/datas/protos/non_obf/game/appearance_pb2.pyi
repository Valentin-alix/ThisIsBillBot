from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CharacterAppearancesRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CharacterAppearancesResponse(_message.Message):
    __slots__ = ("character_faces", "character_colors")
    CHARACTER_FACES_FIELD_NUMBER: _ClassVar[int]
    CHARACTER_COLORS_FIELD_NUMBER: _ClassVar[int]
    character_faces: CharacterFaces
    character_colors: CharacterColors
    def __init__(self, character_faces: _Optional[_Union[CharacterFaces, _Mapping]] = ..., character_colors: _Optional[_Union[CharacterColors, _Mapping]] = ...) -> None: ...

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

class CharacterUpdateFaceRequest(_message.Message):
    __slots__ = ("face_id", "slot")
    FACE_ID_FIELD_NUMBER: _ClassVar[int]
    SLOT_FIELD_NUMBER: _ClassVar[int]
    face_id: int
    slot: int
    def __init__(self, face_id: _Optional[int] = ..., slot: _Optional[int] = ...) -> None: ...

class CharacterFaceUpdatedEvent(_message.Message):
    __slots__ = ("face_id", "slot")
    FACE_ID_FIELD_NUMBER: _ClassVar[int]
    SLOT_FIELD_NUMBER: _ClassVar[int]
    face_id: int
    slot: int
    def __init__(self, face_id: _Optional[int] = ..., slot: _Optional[int] = ...) -> None: ...

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
