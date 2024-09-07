from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

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
    class Result(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ERROR: _ClassVar[MimicryResponse.Result]
        PLAYER_BUSY: _ClassVar[MimicryResponse.Result]
        HOST_NOT_MIMICKABLE: _ClassVar[MimicryResponse.Result]
        HOST_WRAPPED: _ClassVar[MimicryResponse.Result]
        DUPLICATE: _ClassVar[MimicryResponse.Result]
        SUCCESS: _ClassVar[MimicryResponse.Result]
    ERROR: MimicryResponse.Result
    PLAYER_BUSY: MimicryResponse.Result
    HOST_NOT_MIMICKABLE: MimicryResponse.Result
    HOST_WRAPPED: MimicryResponse.Result
    DUPLICATE: MimicryResponse.Result
    SUCCESS: MimicryResponse.Result
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: MimicryResponse.Result
    def __init__(self, result: _Optional[_Union[MimicryResponse.Result, str]] = ...) -> None: ...

class MimicryFreeRequest(_message.Message):
    __slots__ = ("host_uid",)
    HOST_UID_FIELD_NUMBER: _ClassVar[int]
    host_uid: int
    def __init__(self, host_uid: _Optional[int] = ...) -> None: ...

class MimicryFreeResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...
