import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AlterationsEvent(_message.Message):
    __slots__ = ("alterations",)
    ALTERATIONS_FIELD_NUMBER: _ClassVar[int]
    alterations: _containers.RepeatedCompositeFieldContainer[Alteration]
    def __init__(self, alterations: _Optional[_Iterable[_Union[Alteration, _Mapping]]] = ...) -> None: ...

class AlterationAddedEvent(_message.Message):
    __slots__ = ("alteration",)
    ALTERATION_FIELD_NUMBER: _ClassVar[int]
    alteration: Alteration
    def __init__(self, alteration: _Optional[_Union[Alteration, _Mapping]] = ...) -> None: ...

class AlterationRemovedEvent(_message.Message):
    __slots__ = ("alteration",)
    ALTERATION_FIELD_NUMBER: _ClassVar[int]
    alteration: Alteration
    def __init__(self, alteration: _Optional[_Union[Alteration, _Mapping]] = ...) -> None: ...

class AlterationsUpdateEvent(_message.Message):
    __slots__ = ("alterations",)
    ALTERATIONS_FIELD_NUMBER: _ClassVar[int]
    alterations: _containers.RepeatedCompositeFieldContainer[Alteration]
    def __init__(self, alterations: _Optional[_Iterable[_Union[Alteration, _Mapping]]] = ...) -> None: ...

class Alteration(_message.Message):
    __slots__ = ("alteration_id", "creation_time", "expiration_type", "expiration_value", "effects")
    class AlterationExpirationType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN: _ClassVar[Alteration.AlterationExpirationType]
        INFINITE: _ClassVar[Alteration.AlterationExpirationType]
        DATE: _ClassVar[Alteration.AlterationExpirationType]
        FIGHT_COUNT: _ClassVar[Alteration.AlterationExpirationType]
        FIGHTS_WON_COUNT: _ClassVar[Alteration.AlterationExpirationType]
        FIGHTS_LOST_COUNT: _ClassVar[Alteration.AlterationExpirationType]
    UNKNOWN: Alteration.AlterationExpirationType
    INFINITE: Alteration.AlterationExpirationType
    DATE: Alteration.AlterationExpirationType
    FIGHT_COUNT: Alteration.AlterationExpirationType
    FIGHTS_WON_COUNT: Alteration.AlterationExpirationType
    FIGHTS_LOST_COUNT: Alteration.AlterationExpirationType
    ALTERATION_ID_FIELD_NUMBER: _ClassVar[int]
    CREATION_TIME_FIELD_NUMBER: _ClassVar[int]
    EXPIRATION_TYPE_FIELD_NUMBER: _ClassVar[int]
    EXPIRATION_VALUE_FIELD_NUMBER: _ClassVar[int]
    EFFECTS_FIELD_NUMBER: _ClassVar[int]
    alteration_id: int
    creation_time: int
    expiration_type: Alteration.AlterationExpirationType
    expiration_value: int
    effects: _containers.RepeatedCompositeFieldContainer[_common_pb2.ObjectEffect]
    def __init__(self, alteration_id: _Optional[int] = ..., creation_time: _Optional[int] = ..., expiration_type: _Optional[_Union[Alteration.AlterationExpirationType, str]] = ..., expiration_value: _Optional[int] = ..., effects: _Optional[_Iterable[_Union[_common_pb2.ObjectEffect, _Mapping]]] = ...) -> None: ...
