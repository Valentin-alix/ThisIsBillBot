from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class LivingObjectMessageRequest(_message.Message):
    __slots__ = ("message_id", "object_gid")
    MESSAGE_ID_FIELD_NUMBER: _ClassVar[int]
    OBJECT_GID_FIELD_NUMBER: _ClassVar[int]
    message_id: int
    object_gid: int
    def __init__(self, message_id: _Optional[int] = ..., object_gid: _Optional[int] = ...) -> None: ...

class LivingObjectDissociateRequest(_message.Message):
    __slots__ = ("object_uid", "position")
    OBJECT_UID_FIELD_NUMBER: _ClassVar[int]
    POSITION_FIELD_NUMBER: _ClassVar[int]
    object_uid: int
    position: int
    def __init__(self, object_uid: _Optional[int] = ..., position: _Optional[int] = ...) -> None: ...

class LivingObjectChangeSkinRequest(_message.Message):
    __slots__ = ("object_uid", "position", "skin_id")
    OBJECT_UID_FIELD_NUMBER: _ClassVar[int]
    POSITION_FIELD_NUMBER: _ClassVar[int]
    SKIN_ID_FIELD_NUMBER: _ClassVar[int]
    object_uid: int
    position: int
    skin_id: int
    def __init__(self, object_uid: _Optional[int] = ..., position: _Optional[int] = ..., skin_id: _Optional[int] = ...) -> None: ...

class LivingObjectMessageEvent(_message.Message):
    __slots__ = ("message_id", "timestamp", "owner_name", "object_gid")
    MESSAGE_ID_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    OWNER_NAME_FIELD_NUMBER: _ClassVar[int]
    OBJECT_GID_FIELD_NUMBER: _ClassVar[int]
    message_id: int
    timestamp: int
    owner_name: str
    object_gid: int
    def __init__(self, message_id: _Optional[int] = ..., timestamp: _Optional[int] = ..., owner_name: _Optional[str] = ..., object_gid: _Optional[int] = ...) -> None: ...
