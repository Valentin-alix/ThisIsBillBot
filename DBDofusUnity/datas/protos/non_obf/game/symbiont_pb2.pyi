from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MimicryResult(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ERROR: _ClassVar[MimicryResult]
    PLAYER_BUSY: _ClassVar[MimicryResult]
    HOST_NOT_MIMICKABLE: _ClassVar[MimicryResult]
    HOST_WRAPPED: _ClassVar[MimicryResult]
    DUPLICATE: _ClassVar[MimicryResult]
    SUCCESS: _ClassVar[MimicryResult]
ERROR: MimicryResult
PLAYER_BUSY: MimicryResult
HOST_NOT_MIMICKABLE: MimicryResult
HOST_WRAPPED: MimicryResult
DUPLICATE: MimicryResult
SUCCESS: MimicryResult

class WrapperObjectDissociateRequest(_message.Message):
    __slots__ = ("host_uid", "host_position")
    HOST_UID_FIELD_NUMBER: _ClassVar[int]
    HOST_POSITION_FIELD_NUMBER: _ClassVar[int]
    host_uid: int
    host_position: int
    def __init__(self, host_uid: _Optional[int] = ..., host_position: _Optional[int] = ...) -> None: ...

class MimicryRequest(_message.Message):
    __slots__ = ("symbiont_uid", "host_uid")
    SYMBIONT_UID_FIELD_NUMBER: _ClassVar[int]
    HOST_UID_FIELD_NUMBER: _ClassVar[int]
    symbiont_uid: int
    host_uid: int
    def __init__(self, symbiont_uid: _Optional[int] = ..., host_uid: _Optional[int] = ...) -> None: ...

class MimicryResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: MimicryResult
    def __init__(self, result: _Optional[_Union[MimicryResult, str]] = ...) -> None: ...

class MimicryFreeRequest(_message.Message):
    __slots__ = ("host_uid",)
    HOST_UID_FIELD_NUMBER: _ClassVar[int]
    host_uid: int
    def __init__(self, host_uid: _Optional[int] = ...) -> None: ...

class MimicryFreeResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: MimicryResult
    def __init__(self, result: _Optional[_Union[MimicryResult, str]] = ...) -> None: ...
