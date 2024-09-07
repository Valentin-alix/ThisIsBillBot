from com.ankama.dofus.server.game.protocol import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DumpedEntityStatsEvent(_message.Message):
    __slots__ = ("entity_id", "stats")
    ENTITY_ID_FIELD_NUMBER: _ClassVar[int]
    STATS_FIELD_NUMBER: _ClassVar[int]
    entity_id: int
    stats: _containers.RepeatedCompositeFieldContainer[_common_pb2.CharacterCharacteristic]
    def __init__(self, entity_id: _Optional[int] = ..., stats: _Optional[_Iterable[_Union[_common_pb2.CharacterCharacteristic, _Mapping]]] = ...) -> None: ...

class DebugHighlightCellsEvent(_message.Message):
    __slots__ = ("color", "cells")
    COLOR_FIELD_NUMBER: _ClassVar[int]
    CELLS_FIELD_NUMBER: _ClassVar[int]
    color: int
    cells: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, color: _Optional[int] = ..., cells: _Optional[_Iterable[int]] = ...) -> None: ...

class DebugClearHighlightCellsEvent(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class DebugInClientEvent(_message.Message):
    __slots__ = ("level", "message")
    class DebugLevel(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TRACE: _ClassVar[DebugInClientEvent.DebugLevel]
        DEBUG: _ClassVar[DebugInClientEvent.DebugLevel]
        INFO: _ClassVar[DebugInClientEvent.DebugLevel]
        WARN: _ClassVar[DebugInClientEvent.DebugLevel]
        ERROR: _ClassVar[DebugInClientEvent.DebugLevel]
        FATAL: _ClassVar[DebugInClientEvent.DebugLevel]
    TRACE: DebugInClientEvent.DebugLevel
    DEBUG: DebugInClientEvent.DebugLevel
    INFO: DebugInClientEvent.DebugLevel
    WARN: DebugInClientEvent.DebugLevel
    ERROR: DebugInClientEvent.DebugLevel
    FATAL: DebugInClientEvent.DebugLevel
    LEVEL_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    level: DebugInClientEvent.DebugLevel
    message: str
    def __init__(self, level: _Optional[_Union[DebugInClientEvent.DebugLevel, str]] = ..., message: _Optional[str] = ...) -> None: ...
