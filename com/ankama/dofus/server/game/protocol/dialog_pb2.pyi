from com.ankama.dofus.server.game.protocol import common_pb2 as _common_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DialogLeaveRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class DialogLeaveEvent(_message.Message):
    __slots__ = ("dialog_type",)
    DIALOG_TYPE_FIELD_NUMBER: _ClassVar[int]
    dialog_type: _common_pb2.DialogType
    def __init__(self, dialog_type: _Optional[_Union[_common_pb2.DialogType, str]] = ...) -> None: ...

class ChangeAppearanceDialogStart(_message.Message):
    __slots__ = ("type",)
    class AppearanceType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        BODY: _ClassVar[ChangeAppearanceDialogStart.AppearanceType]
        FACE: _ClassVar[ChangeAppearanceDialogStart.AppearanceType]
        COLORS: _ClassVar[ChangeAppearanceDialogStart.AppearanceType]
    BODY: ChangeAppearanceDialogStart.AppearanceType
    FACE: ChangeAppearanceDialogStart.AppearanceType
    COLORS: ChangeAppearanceDialogStart.AppearanceType
    TYPE_FIELD_NUMBER: _ClassVar[int]
    type: ChangeAppearanceDialogStart.AppearanceType
    def __init__(self, type: _Optional[_Union[ChangeAppearanceDialogStart.AppearanceType, str]] = ...) -> None: ...

class ChangeAppearanceDialogLeave(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ChangeAppearanceDialogResult(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...
