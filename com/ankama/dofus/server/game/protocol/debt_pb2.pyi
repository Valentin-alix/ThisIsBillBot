from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DebtsUpdateEvent(_message.Message):
    __slots__ = ("action", "debts")
    class DebtsAction(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DISPATCH: _ClassVar[DebtsUpdateEvent.DebtsAction]
        UPDATE: _ClassVar[DebtsUpdateEvent.DebtsAction]
    DISPATCH: DebtsUpdateEvent.DebtsAction
    UPDATE: DebtsUpdateEvent.DebtsAction
    class DebtInformation(_message.Message):
        __slots__ = ("debt_id", "timestamp", "kamas")
        DEBT_ID_FIELD_NUMBER: _ClassVar[int]
        TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
        KAMAS_FIELD_NUMBER: _ClassVar[int]
        debt_id: int
        timestamp: int
        kamas: int
        def __init__(self, debt_id: _Optional[int] = ..., timestamp: _Optional[int] = ..., kamas: _Optional[int] = ...) -> None: ...
    ACTION_FIELD_NUMBER: _ClassVar[int]
    DEBTS_FIELD_NUMBER: _ClassVar[int]
    action: DebtsUpdateEvent.DebtsAction
    debts: _containers.RepeatedCompositeFieldContainer[DebtsUpdateEvent.DebtInformation]
    def __init__(self, action: _Optional[_Union[DebtsUpdateEvent.DebtsAction, str]] = ..., debts: _Optional[_Iterable[_Union[DebtsUpdateEvent.DebtInformation, _Mapping]]] = ...) -> None: ...

class DebtsDeleteEvent(_message.Message):
    __slots__ = ("reason", "debts")
    class DebtsDeletionReason(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN: _ClassVar[DebtsDeleteEvent.DebtsDeletionReason]
        ADMIN_COMMAND_REQUEST: _ClassVar[DebtsDeleteEvent.DebtsDeletionReason]
        PAYED: _ClassVar[DebtsDeleteEvent.DebtsDeletionReason]
        CANCELED: _ClassVar[DebtsDeleteEvent.DebtsDeletionReason]
    UNKNOWN: DebtsDeleteEvent.DebtsDeletionReason
    ADMIN_COMMAND_REQUEST: DebtsDeleteEvent.DebtsDeletionReason
    PAYED: DebtsDeleteEvent.DebtsDeletionReason
    CANCELED: DebtsDeleteEvent.DebtsDeletionReason
    REASON_FIELD_NUMBER: _ClassVar[int]
    DEBTS_FIELD_NUMBER: _ClassVar[int]
    reason: DebtsDeleteEvent.DebtsDeletionReason
    debts: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, reason: _Optional[_Union[DebtsDeleteEvent.DebtsDeletionReason, str]] = ..., debts: _Optional[_Iterable[int]] = ...) -> None: ...
