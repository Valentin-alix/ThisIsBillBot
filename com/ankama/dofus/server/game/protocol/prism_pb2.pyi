from com.ankama.dofus.server.game.protocol import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PrismTeleportationRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class PrismAttackRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class PrismExchangeRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class PrismRecycleRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class PrismListEvent(_message.Message):
    __slots__ = ("prism_localized_information",)
    PRISM_LOCALIZED_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    prism_localized_information: _containers.RepeatedCompositeFieldContainer[_common_pb2.PrismLocalizedInformation]
    def __init__(self, prism_localized_information: _Optional[_Iterable[_Union[_common_pb2.PrismLocalizedInformation, _Mapping]]] = ...) -> None: ...

class PrismAddOrUpdateEvent(_message.Message):
    __slots__ = ("prism_localized_information",)
    PRISM_LOCALIZED_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    prism_localized_information: _common_pb2.PrismLocalizedInformation
    def __init__(self, prism_localized_information: _Optional[_Union[_common_pb2.PrismLocalizedInformation, _Mapping]] = ...) -> None: ...

class PrismRemoveEvent(_message.Message):
    __slots__ = ("prism_localized_information",)
    PRISM_LOCALIZED_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    prism_localized_information: _common_pb2.PrismLocalizedInformation
    def __init__(self, prism_localized_information: _Optional[_Union[_common_pb2.PrismLocalizedInformation, _Mapping]] = ...) -> None: ...

class PrismAttackedEvent(_message.Message):
    __slots__ = ("prism_localized_information",)
    PRISM_LOCALIZED_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    prism_localized_information: _common_pb2.PrismLocalizedInformation
    def __init__(self, prism_localized_information: _Optional[_Union[_common_pb2.PrismLocalizedInformation, _Mapping]] = ...) -> None: ...

class PrismAttackResultEvent(_message.Message):
    __slots__ = ("prism_localized_information", "prism_attack_result")
    class PrismAttackResult(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DEFENDERS_WIN: _ClassVar[PrismAttackResultEvent.PrismAttackResult]
        ATTACKERS_WIN: _ClassVar[PrismAttackResultEvent.PrismAttackResult]
    DEFENDERS_WIN: PrismAttackResultEvent.PrismAttackResult
    ATTACKERS_WIN: PrismAttackResultEvent.PrismAttackResult
    PRISM_LOCALIZED_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    PRISM_ATTACK_RESULT_FIELD_NUMBER: _ClassVar[int]
    prism_localized_information: _common_pb2.PrismLocalizedInformation
    prism_attack_result: PrismAttackResultEvent.PrismAttackResult
    def __init__(self, prism_localized_information: _Optional[_Union[_common_pb2.PrismLocalizedInformation, _Mapping]] = ..., prism_attack_result: _Optional[_Union[PrismAttackResultEvent.PrismAttackResult, str]] = ...) -> None: ...
