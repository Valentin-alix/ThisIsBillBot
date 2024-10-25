from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CharacterFillSlotFaceRequest(_message.Message):
    __slots__ = ("face",)
    FACE_FIELD_NUMBER: _ClassVar[int]
    face: int
    def __init__(self, face: _Optional[int] = ...) -> None: ...

class CharacterFillSlotFaceResponse(_message.Message):
    __slots__ = ("success", "error")
    class Success(_message.Message):
        __slots__ = ("faceId", "position")
        FACEID_FIELD_NUMBER: _ClassVar[int]
        POSITION_FIELD_NUMBER: _ClassVar[int]
        faceId: int
        position: int
        def __init__(self, faceId: _Optional[int] = ..., position: _Optional[int] = ...) -> None: ...
    class Error(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: CharacterFillSlotFaceResponse.Success
    error: CharacterFillSlotFaceResponse.Error
    def __init__(self, success: _Optional[_Union[CharacterFillSlotFaceResponse.Success, _Mapping]] = ..., error: _Optional[_Union[CharacterFillSlotFaceResponse.Error, _Mapping]] = ...) -> None: ...

class CharacterFillSlotColorsRequest(_message.Message):
    __slots__ = ("colors",)
    COLORS_FIELD_NUMBER: _ClassVar[int]
    colors: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, colors: _Optional[_Iterable[int]] = ...) -> None: ...

class CharacterFillSlotColorsResponse(_message.Message):
    __slots__ = ("success", "error")
    class Success(_message.Message):
        __slots__ = ("colors", "position")
        COLORS_FIELD_NUMBER: _ClassVar[int]
        POSITION_FIELD_NUMBER: _ClassVar[int]
        colors: _containers.RepeatedScalarFieldContainer[int]
        position: int
        def __init__(self, colors: _Optional[_Iterable[int]] = ..., position: _Optional[int] = ...) -> None: ...
    class Error(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: CharacterFillSlotColorsResponse.Success
    error: CharacterFillSlotColorsResponse.Error
    def __init__(self, success: _Optional[_Union[CharacterFillSlotColorsResponse.Success, _Mapping]] = ..., error: _Optional[_Union[CharacterFillSlotColorsResponse.Error, _Mapping]] = ...) -> None: ...
