from com.ankama.dofus.server.game.protocol import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AccessoryPreviewRequest(_message.Message):
    __slots__ = ("object_gid", "show_current_objects")
    OBJECT_GID_FIELD_NUMBER: _ClassVar[int]
    SHOW_CURRENT_OBJECTS_FIELD_NUMBER: _ClassVar[int]
    object_gid: _containers.RepeatedScalarFieldContainer[int]
    show_current_objects: bool
    def __init__(self, object_gid: _Optional[_Iterable[int]] = ..., show_current_objects: bool = ...) -> None: ...

class AccessoryPreviewErrorEvent(_message.Message):
    __slots__ = ("error",)
    class AccessoryPreviewError(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ERROR: _ClassVar[AccessoryPreviewErrorEvent.AccessoryPreviewError]
        COOL_DOWN: _ClassVar[AccessoryPreviewErrorEvent.AccessoryPreviewError]
        BAD_ITEM: _ClassVar[AccessoryPreviewErrorEvent.AccessoryPreviewError]
    ERROR: AccessoryPreviewErrorEvent.AccessoryPreviewError
    COOL_DOWN: AccessoryPreviewErrorEvent.AccessoryPreviewError
    BAD_ITEM: AccessoryPreviewErrorEvent.AccessoryPreviewError
    ERROR_FIELD_NUMBER: _ClassVar[int]
    error: AccessoryPreviewErrorEvent.AccessoryPreviewError
    def __init__(self, error: _Optional[_Union[AccessoryPreviewErrorEvent.AccessoryPreviewError, str]] = ...) -> None: ...

class AccessoryPreviewEvent(_message.Message):
    __slots__ = ("look",)
    LOOK_FIELD_NUMBER: _ClassVar[int]
    look: _common_pb2.EntityLook
    def __init__(self, look: _Optional[_Union[_common_pb2.EntityLook, _Mapping]] = ...) -> None: ...
