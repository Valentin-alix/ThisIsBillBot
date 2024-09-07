from com.ankama.dofus.server.game.protocol import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PlayerStatusUpdateRequest(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: _common_pb2.CharacterStatus
    def __init__(self, status: _Optional[_Union[_common_pb2.CharacterStatus, _Mapping]] = ...) -> None: ...

class ResetCharacterCharacteristicsRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class FreeSoulRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CharacterCharacteristicUpgradeRequest(_message.Message):
    __slots__ = ("strength", "vitality", "wisdom", "chance", "agility", "intelligence")
    STRENGTH_FIELD_NUMBER: _ClassVar[int]
    VITALITY_FIELD_NUMBER: _ClassVar[int]
    WISDOM_FIELD_NUMBER: _ClassVar[int]
    CHANCE_FIELD_NUMBER: _ClassVar[int]
    AGILITY_FIELD_NUMBER: _ClassVar[int]
    INTELLIGENCE_FIELD_NUMBER: _ClassVar[int]
    strength: int
    vitality: int
    wisdom: int
    chance: int
    agility: int
    intelligence: int
    def __init__(self, strength: _Optional[int] = ..., vitality: _Optional[int] = ..., wisdom: _Optional[int] = ..., chance: _Optional[int] = ..., agility: _Optional[int] = ..., intelligence: _Optional[int] = ...) -> None: ...

class PlayerStatusUpdateErrorEvent(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class PlayerStatusUpdatedEvent(_message.Message):
    __slots__ = ("account_id", "player_id", "status")
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    account_id: int
    player_id: int
    status: _common_pb2.CharacterStatus
    def __init__(self, account_id: _Optional[int] = ..., player_id: _Optional[int] = ..., status: _Optional[_Union[_common_pb2.CharacterStatus, _Mapping]] = ...) -> None: ...

class CharacterCharacteristicsEvent(_message.Message):
    __slots__ = ("stats",)
    STATS_FIELD_NUMBER: _ClassVar[int]
    stats: _common_pb2.CharacterCharacteristics
    def __init__(self, stats: _Optional[_Union[_common_pb2.CharacterCharacteristics, _Mapping]] = ...) -> None: ...

class CharacterLevelUpEvent(_message.Message):
    __slots__ = ("new_level",)
    NEW_LEVEL_FIELD_NUMBER: _ClassVar[int]
    new_level: int
    def __init__(self, new_level: _Optional[int] = ...) -> None: ...

class CharacterExperienceGainEvent(_message.Message):
    __slots__ = ("character_experience", "mount_experience", "guild_experience")
    CHARACTER_EXPERIENCE_FIELD_NUMBER: _ClassVar[int]
    MOUNT_EXPERIENCE_FIELD_NUMBER: _ClassVar[int]
    GUILD_EXPERIENCE_FIELD_NUMBER: _ClassVar[int]
    character_experience: int
    mount_experience: int
    guild_experience: int
    def __init__(self, character_experience: _Optional[int] = ..., mount_experience: _Optional[int] = ..., guild_experience: _Optional[int] = ...) -> None: ...

class LifePointsRegenBeginEvent(_message.Message):
    __slots__ = ("regen_rate",)
    REGEN_RATE_FIELD_NUMBER: _ClassVar[int]
    regen_rate: int
    def __init__(self, regen_rate: _Optional[int] = ...) -> None: ...

class UpdateLifePointsEvent(_message.Message):
    __slots__ = ("life_points", "max_life_points", "life_points_gained")
    LIFE_POINTS_FIELD_NUMBER: _ClassVar[int]
    MAX_LIFE_POINTS_FIELD_NUMBER: _ClassVar[int]
    LIFE_POINTS_GAINED_FIELD_NUMBER: _ClassVar[int]
    life_points: int
    max_life_points: int
    life_points_gained: int
    def __init__(self, life_points: _Optional[int] = ..., max_life_points: _Optional[int] = ..., life_points_gained: _Optional[int] = ...) -> None: ...

class CharacterLifeStatusEvent(_message.Message):
    __slots__ = ("state", "phoenix_map_id")
    class LifeStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ALIVE_AND_KICKING: _ClassVar[CharacterLifeStatusEvent.LifeStatus]
        TOMBSTONE: _ClassVar[CharacterLifeStatusEvent.LifeStatus]
        PHANTOM: _ClassVar[CharacterLifeStatusEvent.LifeStatus]
    ALIVE_AND_KICKING: CharacterLifeStatusEvent.LifeStatus
    TOMBSTONE: CharacterLifeStatusEvent.LifeStatus
    PHANTOM: CharacterLifeStatusEvent.LifeStatus
    STATE_FIELD_NUMBER: _ClassVar[int]
    PHOENIX_MAP_ID_FIELD_NUMBER: _ClassVar[int]
    state: CharacterLifeStatusEvent.LifeStatus
    phoenix_map_id: int
    def __init__(self, state: _Optional[_Union[CharacterLifeStatusEvent.LifeStatus, str]] = ..., phoenix_map_id: _Optional[int] = ...) -> None: ...

class GameOverEvent(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CharacterCharacteristicUpgradeResultEvent(_message.Message):
    __slots__ = ("result", "points")
    class CharacteristicUpgradeResult(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        NONE: _ClassVar[CharacterCharacteristicUpgradeResultEvent.CharacteristicUpgradeResult]
        SUCCESS: _ClassVar[CharacterCharacteristicUpgradeResultEvent.CharacteristicUpgradeResult]
        GUEST: _ClassVar[CharacterCharacteristicUpgradeResultEvent.CharacteristicUpgradeResult]
        IN_FIGHT: _ClassVar[CharacterCharacteristicUpgradeResultEvent.CharacteristicUpgradeResult]
        NOT_ENOUGH_POINT: _ClassVar[CharacterCharacteristicUpgradeResultEvent.CharacteristicUpgradeResult]
    NONE: CharacterCharacteristicUpgradeResultEvent.CharacteristicUpgradeResult
    SUCCESS: CharacterCharacteristicUpgradeResultEvent.CharacteristicUpgradeResult
    GUEST: CharacterCharacteristicUpgradeResultEvent.CharacteristicUpgradeResult
    IN_FIGHT: CharacterCharacteristicUpgradeResultEvent.CharacteristicUpgradeResult
    NOT_ENOUGH_POINT: CharacterCharacteristicUpgradeResultEvent.CharacteristicUpgradeResult
    RESULT_FIELD_NUMBER: _ClassVar[int]
    POINTS_FIELD_NUMBER: _ClassVar[int]
    result: CharacterCharacteristicUpgradeResultEvent.CharacteristicUpgradeResult
    points: int
    def __init__(self, result: _Optional[_Union[CharacterCharacteristicUpgradeResultEvent.CharacteristicUpgradeResult, str]] = ..., points: _Optional[int] = ...) -> None: ...

class CharacterRestrictionsEvent(_message.Message):
    __slots__ = ("character_id", "restrictions")
    CHARACTER_ID_FIELD_NUMBER: _ClassVar[int]
    RESTRICTIONS_FIELD_NUMBER: _ClassVar[int]
    character_id: int
    restrictions: _containers.RepeatedScalarFieldContainer[_common_pb2.Restriction]
    def __init__(self, character_id: _Optional[int] = ..., restrictions: _Optional[_Iterable[_Union[_common_pb2.Restriction, str]]] = ...) -> None: ...

class CharacterOnConnectionEvent(_message.Message):
    __slots__ = ("connection_event",)
    class ConnectionEvent(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        FIRST_ACCOUNT_CONNECTION_EVER: _ClassVar[CharacterOnConnectionEvent.ConnectionEvent]
        FIRST_ACCOUNT_CONNECTION_ON_SERVER: _ClassVar[CharacterOnConnectionEvent.ConnectionEvent]
        FIRST_ACCOUNT_CONNECTION_SINCE_REBOOT: _ClassVar[CharacterOnConnectionEvent.ConnectionEvent]
        FIRST_CHARACTER_CONNECTION: _ClassVar[CharacterOnConnectionEvent.ConnectionEvent]
        FIRST_CHARACTER_CONNECTION_SINCE_REBOOT: _ClassVar[CharacterOnConnectionEvent.ConnectionEvent]
    FIRST_ACCOUNT_CONNECTION_EVER: CharacterOnConnectionEvent.ConnectionEvent
    FIRST_ACCOUNT_CONNECTION_ON_SERVER: CharacterOnConnectionEvent.ConnectionEvent
    FIRST_ACCOUNT_CONNECTION_SINCE_REBOOT: CharacterOnConnectionEvent.ConnectionEvent
    FIRST_CHARACTER_CONNECTION: CharacterOnConnectionEvent.ConnectionEvent
    FIRST_CHARACTER_CONNECTION_SINCE_REBOOT: CharacterOnConnectionEvent.ConnectionEvent
    CONNECTION_EVENT_FIELD_NUMBER: _ClassVar[int]
    connection_event: CharacterOnConnectionEvent.ConnectionEvent
    def __init__(self, connection_event: _Optional[_Union[CharacterOnConnectionEvent.ConnectionEvent, str]] = ...) -> None: ...
