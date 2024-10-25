import common_pb2 as _common_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CompassType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SIMPLE: _ClassVar[CompassType]
    SPOUSE: _ClassVar[CompassType]
    PARTY: _ClassVar[CompassType]
    PVP_SEEK: _ClassVar[CompassType]
    QUEST: _ClassVar[CompassType]
SIMPLE: CompassType
SPOUSE: CompassType
PARTY: CompassType
PVP_SEEK: CompassType
QUEST: CompassType

class CompassResetEvent(_message.Message):
    __slots__ = ("type",)
    TYPE_FIELD_NUMBER: _ClassVar[int]
    type: CompassType
    def __init__(self, type: _Optional[_Union[CompassType, str]] = ...) -> None: ...

class CompassUpdateEvent(_message.Message):
    __slots__ = ("type", "coordinates", "party_member", "pvp_seek")
    class PartyMember(_message.Message):
        __slots__ = ("member_id", "active")
        MEMBER_ID_FIELD_NUMBER: _ClassVar[int]
        ACTIVE_FIELD_NUMBER: _ClassVar[int]
        member_id: int
        active: bool
        def __init__(self, member_id: _Optional[int] = ..., active: bool = ...) -> None: ...
    class PvpSeek(_message.Message):
        __slots__ = ("target_id", "target_name")
        TARGET_ID_FIELD_NUMBER: _ClassVar[int]
        TARGET_NAME_FIELD_NUMBER: _ClassVar[int]
        target_id: int
        target_name: str
        def __init__(self, target_id: _Optional[int] = ..., target_name: _Optional[str] = ...) -> None: ...
    TYPE_FIELD_NUMBER: _ClassVar[int]
    COORDINATES_FIELD_NUMBER: _ClassVar[int]
    PARTY_MEMBER_FIELD_NUMBER: _ClassVar[int]
    PVP_SEEK_FIELD_NUMBER: _ClassVar[int]
    type: CompassType
    coordinates: _common_pb2.MapCoordinates
    party_member: CompassUpdateEvent.PartyMember
    pvp_seek: CompassUpdateEvent.PvpSeek
    def __init__(self, type: _Optional[_Union[CompassType, str]] = ..., coordinates: _Optional[_Union[_common_pb2.MapCoordinates, _Mapping]] = ..., party_member: _Optional[_Union[CompassUpdateEvent.PartyMember, _Mapping]] = ..., pvp_seek: _Optional[_Union[CompassUpdateEvent.PvpSeek, _Mapping]] = ...) -> None: ...
