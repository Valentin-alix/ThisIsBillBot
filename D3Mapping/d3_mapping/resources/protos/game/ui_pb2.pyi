from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ClientUIOpenedEvent(_message.Message):
    __slots__ = ("type", "object_uid")
    class UIType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNDEFINED: _ClassVar[ClientUIOpenedEvent.UIType]
        TELEPORT_GUILD_HOUSE: _ClassVar[ClientUIOpenedEvent.UIType]
        TELEPORT_GUILD_PADDOCK: _ClassVar[ClientUIOpenedEvent.UIType]
        OBJECT_MIMICRY: _ClassVar[ClientUIOpenedEvent.UIType]
        LEGENDARY_TREASURE_QUEST: _ClassVar[ClientUIOpenedEvent.UIType]
        TELEPORT_HOUSE: _ClassVar[ClientUIOpenedEvent.UIType]
    UNDEFINED: ClientUIOpenedEvent.UIType
    TELEPORT_GUILD_HOUSE: ClientUIOpenedEvent.UIType
    TELEPORT_GUILD_PADDOCK: ClientUIOpenedEvent.UIType
    OBJECT_MIMICRY: ClientUIOpenedEvent.UIType
    LEGENDARY_TREASURE_QUEST: ClientUIOpenedEvent.UIType
    TELEPORT_HOUSE: ClientUIOpenedEvent.UIType
    TYPE_FIELD_NUMBER: _ClassVar[int]
    OBJECT_UID_FIELD_NUMBER: _ClassVar[int]
    type: ClientUIOpenedEvent.UIType
    object_uid: int
    def __init__(self, type: _Optional[_Union[ClientUIOpenedEvent.UIType, str]] = ..., object_uid: _Optional[int] = ...) -> None: ...
