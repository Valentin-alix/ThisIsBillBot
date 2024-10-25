from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Teleporter(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TELEPORTER_ZAAP: _ClassVar[Teleporter]
    TELEPORTER_SUBWAY: _ClassVar[Teleporter]
    TELEPORTER_PRISM: _ClassVar[Teleporter]
    TELEPORTER_HAVEN_BAG: _ClassVar[Teleporter]
    TELEPORTER_ANOMALY: _ClassVar[Teleporter]
TELEPORTER_ZAAP: Teleporter
TELEPORTER_SUBWAY: Teleporter
TELEPORTER_PRISM: Teleporter
TELEPORTER_HAVEN_BAG: Teleporter
TELEPORTER_ANOMALY: Teleporter

class TeleportRequest(_message.Message):
    __slots__ = ("source_type", "destination_type", "map_id")
    SOURCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    DESTINATION_TYPE_FIELD_NUMBER: _ClassVar[int]
    MAP_ID_FIELD_NUMBER: _ClassVar[int]
    source_type: Teleporter
    destination_type: Teleporter
    map_id: int
    def __init__(self, source_type: _Optional[_Union[Teleporter, str]] = ..., destination_type: _Optional[_Union[Teleporter, str]] = ..., map_id: _Optional[int] = ...) -> None: ...

class ZaapRespawnSaveRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class TeleportBuddiesAnswerRequest(_message.Message):
    __slots__ = ("accept",)
    ACCEPT_FIELD_NUMBER: _ClassVar[int]
    accept: bool
    def __init__(self, accept: bool = ...) -> None: ...

class TeleportToBuddyAnswerRequest(_message.Message):
    __slots__ = ("accept",)
    ACCEPT_FIELD_NUMBER: _ClassVar[int]
    accept: bool
    def __init__(self, accept: bool = ...) -> None: ...

class TeleportPlayerAnswerRequest(_message.Message):
    __slots__ = ("accept",)
    ACCEPT_FIELD_NUMBER: _ClassVar[int]
    accept: bool
    def __init__(self, accept: bool = ...) -> None: ...

class GroupTeleportPlayerAnswerRequest(_message.Message):
    __slots__ = ("accept",)
    ACCEPT_FIELD_NUMBER: _ClassVar[int]
    accept: bool
    def __init__(self, accept: bool = ...) -> None: ...

class ZaapRespawnUpdatedEvent(_message.Message):
    __slots__ = ("map_id",)
    MAP_ID_FIELD_NUMBER: _ClassVar[int]
    map_id: int
    def __init__(self, map_id: _Optional[int] = ...) -> None: ...

class TeleportDestinationsEvent(_message.Message):
    __slots__ = ("type", "destinations", "spawn_map_id")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    DESTINATIONS_FIELD_NUMBER: _ClassVar[int]
    SPAWN_MAP_ID_FIELD_NUMBER: _ClassVar[int]
    type: Teleporter
    destinations: _containers.RepeatedCompositeFieldContainer[TeleportDestination]
    spawn_map_id: int
    def __init__(self, type: _Optional[_Union[Teleporter, str]] = ..., destinations: _Optional[_Iterable[_Union[TeleportDestination, _Mapping]]] = ..., spawn_map_id: _Optional[int] = ...) -> None: ...

class ZaapKnownListEvent(_message.Message):
    __slots__ = ("destinations",)
    DESTINATIONS_FIELD_NUMBER: _ClassVar[int]
    destinations: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, destinations: _Optional[_Iterable[int]] = ...) -> None: ...

class TeleportBuddiesEvent(_message.Message):
    __slots__ = ("dungeon_id",)
    DUNGEON_ID_FIELD_NUMBER: _ClassVar[int]
    dungeon_id: int
    def __init__(self, dungeon_id: _Optional[int] = ...) -> None: ...

class TeleportBuddiesRequestedEvent(_message.Message):
    __slots__ = ("dungeon_id", "inviter_id", "invalid_buddies_id")
    DUNGEON_ID_FIELD_NUMBER: _ClassVar[int]
    INVITER_ID_FIELD_NUMBER: _ClassVar[int]
    INVALID_BUDDIES_ID_FIELD_NUMBER: _ClassVar[int]
    dungeon_id: int
    inviter_id: int
    invalid_buddies_id: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, dungeon_id: _Optional[int] = ..., inviter_id: _Optional[int] = ..., invalid_buddies_id: _Optional[_Iterable[int]] = ...) -> None: ...

class TeleportToBuddyOfferEvent(_message.Message):
    __slots__ = ("dungeon_id", "buddy_id", "time_left")
    DUNGEON_ID_FIELD_NUMBER: _ClassVar[int]
    BUDDY_ID_FIELD_NUMBER: _ClassVar[int]
    TIME_LEFT_FIELD_NUMBER: _ClassVar[int]
    dungeon_id: int
    buddy_id: int
    time_left: int
    def __init__(self, dungeon_id: _Optional[int] = ..., buddy_id: _Optional[int] = ..., time_left: _Optional[int] = ...) -> None: ...

class TeleportToBuddyClosedEvent(_message.Message):
    __slots__ = ("dungeon_id", "buddy_id")
    DUNGEON_ID_FIELD_NUMBER: _ClassVar[int]
    BUDDY_ID_FIELD_NUMBER: _ClassVar[int]
    dungeon_id: int
    buddy_id: int
    def __init__(self, dungeon_id: _Optional[int] = ..., buddy_id: _Optional[int] = ...) -> None: ...

class TeleportPlayerOfferEvent(_message.Message):
    __slots__ = ("map_id", "message", "time_left", "requester_id")
    MAP_ID_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    TIME_LEFT_FIELD_NUMBER: _ClassVar[int]
    REQUESTER_ID_FIELD_NUMBER: _ClassVar[int]
    map_id: int
    message: str
    time_left: int
    requester_id: int
    def __init__(self, map_id: _Optional[int] = ..., message: _Optional[str] = ..., time_left: _Optional[int] = ..., requester_id: _Optional[int] = ...) -> None: ...

class TeleportPlayerClosedEvent(_message.Message):
    __slots__ = ("map_id", "requester_id")
    MAP_ID_FIELD_NUMBER: _ClassVar[int]
    REQUESTER_ID_FIELD_NUMBER: _ClassVar[int]
    map_id: int
    requester_id: int
    def __init__(self, map_id: _Optional[int] = ..., requester_id: _Optional[int] = ...) -> None: ...

class GroupTeleportPlayerOfferEvent(_message.Message):
    __slots__ = ("map_id", "world_x", "world_y", "time_left", "requester_id", "requester_name")
    MAP_ID_FIELD_NUMBER: _ClassVar[int]
    WORLD_X_FIELD_NUMBER: _ClassVar[int]
    WORLD_Y_FIELD_NUMBER: _ClassVar[int]
    TIME_LEFT_FIELD_NUMBER: _ClassVar[int]
    REQUESTER_ID_FIELD_NUMBER: _ClassVar[int]
    REQUESTER_NAME_FIELD_NUMBER: _ClassVar[int]
    map_id: int
    world_x: int
    world_y: int
    time_left: int
    requester_id: int
    requester_name: str
    def __init__(self, map_id: _Optional[int] = ..., world_x: _Optional[int] = ..., world_y: _Optional[int] = ..., time_left: _Optional[int] = ..., requester_id: _Optional[int] = ..., requester_name: _Optional[str] = ...) -> None: ...

class GroupTeleportPlayerClosedEvent(_message.Message):
    __slots__ = ("map_id", "requester_id")
    MAP_ID_FIELD_NUMBER: _ClassVar[int]
    REQUESTER_ID_FIELD_NUMBER: _ClassVar[int]
    map_id: int
    requester_id: int
    def __init__(self, map_id: _Optional[int] = ..., requester_id: _Optional[int] = ...) -> None: ...

class TeleportDestination(_message.Message):
    __slots__ = ("type", "map_id", "subarea_id", "level", "cost", "anomaly")
    class Anomaly(_message.Message):
        __slots__ = ("bonus_pourcentage", "remaining_time")
        BONUS_POURCENTAGE_FIELD_NUMBER: _ClassVar[int]
        REMAINING_TIME_FIELD_NUMBER: _ClassVar[int]
        bonus_pourcentage: int
        remaining_time: int
        def __init__(self, bonus_pourcentage: _Optional[int] = ..., remaining_time: _Optional[int] = ...) -> None: ...
    TYPE_FIELD_NUMBER: _ClassVar[int]
    MAP_ID_FIELD_NUMBER: _ClassVar[int]
    SUBAREA_ID_FIELD_NUMBER: _ClassVar[int]
    LEVEL_FIELD_NUMBER: _ClassVar[int]
    COST_FIELD_NUMBER: _ClassVar[int]
    ANOMALY_FIELD_NUMBER: _ClassVar[int]
    type: Teleporter
    map_id: int
    subarea_id: int
    level: int
    cost: int
    anomaly: TeleportDestination.Anomaly
    def __init__(self, type: _Optional[_Union[Teleporter, str]] = ..., map_id: _Optional[int] = ..., subarea_id: _Optional[int] = ..., level: _Optional[int] = ..., cost: _Optional[int] = ..., anomaly: _Optional[_Union[TeleportDestination.Anomaly, _Mapping]] = ...) -> None: ...
