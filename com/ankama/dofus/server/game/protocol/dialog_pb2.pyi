from com.ankama.dofus.server.game.protocol import common_pb2 as _common_pb2
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
