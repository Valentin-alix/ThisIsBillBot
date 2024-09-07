from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class SubareaRewardRateEvent(_message.Message):
    __slots__ = ("subarea_rate",)
    SUBAREA_RATE_FIELD_NUMBER: _ClassVar[int]
    subarea_rate: int
    def __init__(self, subarea_rate: _Optional[int] = ...) -> None: ...

class AreaFightModifierUpdateEvent(_message.Message):
    __slots__ = ("spell_pairs",)
    SPELL_PAIRS_FIELD_NUMBER: _ClassVar[int]
    spell_pairs: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, spell_pairs: _Optional[_Iterable[int]] = ...) -> None: ...
