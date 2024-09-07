from com.ankama.dofus.server.game.protocol import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GuildHousesEvent(_message.Message):
    __slots__ = ("houses",)
    HOUSES_FIELD_NUMBER: _ClassVar[int]
    houses: _containers.RepeatedCompositeFieldContainer[_common_pb2.House]
    def __init__(self, houses: _Optional[_Iterable[_Union[_common_pb2.House, _Mapping]]] = ...) -> None: ...

class GuildHouseUpdateEvent(_message.Message):
    __slots__ = ("house",)
    HOUSE_FIELD_NUMBER: _ClassVar[int]
    house: _common_pb2.House
    def __init__(self, house: _Optional[_Union[_common_pb2.House, _Mapping]] = ...) -> None: ...

class GuildHouseRemoveEvent(_message.Message):
    __slots__ = ("house_id", "instance_id", "second_hand")
    HOUSE_ID_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_ID_FIELD_NUMBER: _ClassVar[int]
    SECOND_HAND_FIELD_NUMBER: _ClassVar[int]
    house_id: int
    instance_id: int
    second_hand: bool
    def __init__(self, house_id: _Optional[int] = ..., instance_id: _Optional[int] = ..., second_hand: bool = ...) -> None: ...
