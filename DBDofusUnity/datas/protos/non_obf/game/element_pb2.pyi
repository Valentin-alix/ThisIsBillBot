from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class LockableUseCodeRequest(_message.Message):
    __slots__ = ("code",)
    CODE_FIELD_NUMBER: _ClassVar[int]
    code: str
    def __init__(self, code: _Optional[str] = ...) -> None: ...

class LockableChangeCodeRequest(_message.Message):
    __slots__ = ("code",)
    CODE_FIELD_NUMBER: _ClassVar[int]
    code: str
    def __init__(self, code: _Optional[str] = ...) -> None: ...

class PurchasableDialogEvent(_message.Message):
    __slots__ = ("action", "purchasable_id", "purchasable_instance_id", "second_hand", "price")
    class Action(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        BUY: _ClassVar[PurchasableDialogEvent.Action]
        SELL: _ClassVar[PurchasableDialogEvent.Action]
    BUY: PurchasableDialogEvent.Action
    SELL: PurchasableDialogEvent.Action
    ACTION_FIELD_NUMBER: _ClassVar[int]
    PURCHASABLE_ID_FIELD_NUMBER: _ClassVar[int]
    PURCHASABLE_INSTANCE_ID_FIELD_NUMBER: _ClassVar[int]
    SECOND_HAND_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    action: PurchasableDialogEvent.Action
    purchasable_id: int
    purchasable_instance_id: int
    second_hand: bool
    price: int
    def __init__(self, action: _Optional[_Union[PurchasableDialogEvent.Action, str]] = ..., purchasable_id: _Optional[int] = ..., purchasable_instance_id: _Optional[int] = ..., second_hand: bool = ..., price: _Optional[int] = ...) -> None: ...

class LockableShowCodeDialogEvent(_message.Message):
    __slots__ = ("action", "code_size")
    class Action(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        CHANGE: _ClassVar[LockableShowCodeDialogEvent.Action]
        USE: _ClassVar[LockableShowCodeDialogEvent.Action]
    CHANGE: LockableShowCodeDialogEvent.Action
    USE: LockableShowCodeDialogEvent.Action
    ACTION_FIELD_NUMBER: _ClassVar[int]
    CODE_SIZE_FIELD_NUMBER: _ClassVar[int]
    action: LockableShowCodeDialogEvent.Action
    code_size: int
    def __init__(self, action: _Optional[_Union[LockableShowCodeDialogEvent.Action, str]] = ..., code_size: _Optional[int] = ...) -> None: ...

class LockableCodeResultEvent(_message.Message):
    __slots__ = ("result",)
    class LockableResult(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNLOCKED: _ClassVar[LockableCodeResultEvent.LockableResult]
        CODE_ERROR: _ClassVar[LockableCodeResultEvent.LockableResult]
        UNLOCK_FORBIDDEN: _ClassVar[LockableCodeResultEvent.LockableResult]
    UNLOCKED: LockableCodeResultEvent.LockableResult
    CODE_ERROR: LockableCodeResultEvent.LockableResult
    UNLOCK_FORBIDDEN: LockableCodeResultEvent.LockableResult
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: LockableCodeResultEvent.LockableResult
    def __init__(self, result: _Optional[_Union[LockableCodeResultEvent.LockableResult, str]] = ...) -> None: ...

class LockableStateUpdateHouseDoorEvent(_message.Message):
    __slots__ = ("house_id", "house_instance_id", "second_hand", "locked")
    HOUSE_ID_FIELD_NUMBER: _ClassVar[int]
    HOUSE_INSTANCE_ID_FIELD_NUMBER: _ClassVar[int]
    SECOND_HAND_FIELD_NUMBER: _ClassVar[int]
    LOCKED_FIELD_NUMBER: _ClassVar[int]
    house_id: int
    house_instance_id: int
    second_hand: bool
    locked: bool
    def __init__(self, house_id: _Optional[int] = ..., house_instance_id: _Optional[int] = ..., second_hand: bool = ..., locked: bool = ...) -> None: ...
