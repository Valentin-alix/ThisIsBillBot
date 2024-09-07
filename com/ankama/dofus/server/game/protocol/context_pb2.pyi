from com.ankama.dofus.server.game.protocol import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ContextCreationRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ContextReadyRequest(_message.Message):
    __slots__ = ("map_id",)
    MAP_ID_FIELD_NUMBER: _ClassVar[int]
    map_id: int
    def __init__(self, map_id: _Optional[int] = ...) -> None: ...

class ContextQuitRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ContextKickRequest(_message.Message):
    __slots__ = ("target_id",)
    TARGET_ID_FIELD_NUMBER: _ClassVar[int]
    target_id: int
    def __init__(self, target_id: _Optional[int] = ...) -> None: ...

class ShowCellRequest(_message.Message):
    __slots__ = ("cell_id",)
    CELL_ID_FIELD_NUMBER: _ClassVar[int]
    cell_id: int
    def __init__(self, cell_id: _Optional[int] = ...) -> None: ...

class ContextCreationEvent(_message.Message):
    __slots__ = ("context",)
    class GameContext(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ROLE_PLAY: _ClassVar[ContextCreationEvent.GameContext]
        FIGHT: _ClassVar[ContextCreationEvent.GameContext]
    ROLE_PLAY: ContextCreationEvent.GameContext
    FIGHT: ContextCreationEvent.GameContext
    CONTEXT_FIELD_NUMBER: _ClassVar[int]
    context: ContextCreationEvent.GameContext
    def __init__(self, context: _Optional[_Union[ContextCreationEvent.GameContext, str]] = ...) -> None: ...

class ContextDestroyEvent(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ContextRemoveElementEvent(_message.Message):
    __slots__ = ("element_id",)
    ELEMENT_ID_FIELD_NUMBER: _ClassVar[int]
    element_id: int
    def __init__(self, element_id: _Optional[int] = ...) -> None: ...

class ContextRemoveElementsEvent(_message.Message):
    __slots__ = ("element_id",)
    ELEMENT_ID_FIELD_NUMBER: _ClassVar[int]
    element_id: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, element_id: _Optional[_Iterable[int]] = ...) -> None: ...

class ContextRefreshEntityLookEvent(_message.Message):
    __slots__ = ("entity_id", "look")
    ENTITY_ID_FIELD_NUMBER: _ClassVar[int]
    LOOK_FIELD_NUMBER: _ClassVar[int]
    entity_id: int
    look: _common_pb2.EntityLook
    def __init__(self, entity_id: _Optional[int] = ..., look: _Optional[_Union[_common_pb2.EntityLook, _Mapping]] = ...) -> None: ...

class EntitiesDispositionEvent(_message.Message):
    __slots__ = ("dispositions",)
    DISPOSITIONS_FIELD_NUMBER: _ClassVar[int]
    dispositions: _containers.RepeatedCompositeFieldContainer[_common_pb2.EntityDisposition]
    def __init__(self, dispositions: _Optional[_Iterable[_Union[_common_pb2.EntityDisposition, _Mapping]]] = ...) -> None: ...

class EntityDispositionErrorEvent(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class MonsterBoosts(_message.Message):
    __slots__ = ("id", "xp_boost", "drop_boost")
    ID_FIELD_NUMBER: _ClassVar[int]
    XP_BOOST_FIELD_NUMBER: _ClassVar[int]
    DROP_BOOST_FIELD_NUMBER: _ClassVar[int]
    id: int
    xp_boost: int
    drop_boost: int
    def __init__(self, id: _Optional[int] = ..., xp_boost: _Optional[int] = ..., drop_boost: _Optional[int] = ...) -> None: ...

class RefreshMonsterBoostsEvent(_message.Message):
    __slots__ = ("monster_boosts", "family_boosts")
    MONSTER_BOOSTS_FIELD_NUMBER: _ClassVar[int]
    FAMILY_BOOSTS_FIELD_NUMBER: _ClassVar[int]
    monster_boosts: _containers.RepeatedCompositeFieldContainer[MonsterBoosts]
    family_boosts: _containers.RepeatedCompositeFieldContainer[MonsterBoosts]
    def __init__(self, monster_boosts: _Optional[_Iterable[_Union[MonsterBoosts, _Mapping]]] = ..., family_boosts: _Optional[_Iterable[_Union[MonsterBoosts, _Mapping]]] = ...) -> None: ...

class ShowCellEvent(_message.Message):
    __slots__ = ("source_id", "cell_id")
    SOURCE_ID_FIELD_NUMBER: _ClassVar[int]
    CELL_ID_FIELD_NUMBER: _ClassVar[int]
    source_id: int
    cell_id: int
    def __init__(self, source_id: _Optional[int] = ..., cell_id: _Optional[int] = ...) -> None: ...
