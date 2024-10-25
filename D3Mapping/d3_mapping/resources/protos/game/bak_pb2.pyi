from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class BidAction(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    BID_INVALID_ACTION: _ClassVar[BidAction]
    BID_CONSUME_BUFF: _ClassVar[BidAction]
    BID_CANCEL: _ClassVar[BidAction]
    BID_CREATE_KAMA: _ClassVar[BidAction]
    BID_CREATE_OGRINE: _ClassVar[BidAction]
    BID_BUY_KAMA: _ClassVar[BidAction]
    BID_BUY_OGRINE: _ClassVar[BidAction]
BID_INVALID_ACTION: BidAction
BID_CONSUME_BUFF: BidAction
BID_CANCEL: BidAction
BID_CREATE_KAMA: BidAction
BID_CREATE_OGRINE: BidAction
BID_BUY_KAMA: BidAction
BID_BUY_OGRINE: BidAction

class BufferInformation(_message.Message):
    __slots__ = ("buffer_id", "buffer_amount")
    BUFFER_ID_FIELD_NUMBER: _ClassVar[int]
    BUFFER_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    buffer_id: int
    buffer_amount: int
    def __init__(self, buffer_id: _Optional[int] = ..., buffer_amount: _Optional[int] = ...) -> None: ...

class BakBufferListRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class BakBufferListEvent(_message.Message):
    __slots__ = ("buffers",)
    BUFFERS_FIELD_NUMBER: _ClassVar[int]
    buffers: _containers.RepeatedCompositeFieldContainer[BufferInformation]
    def __init__(self, buffers: _Optional[_Iterable[_Union[BufferInformation, _Mapping]]] = ...) -> None: ...

class BakConsumeBufferRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class BakCancelBidRequest(_message.Message):
    __slots__ = ("bid_id", "bid_cancellation_type")
    class BidCancellationType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN_TYPE: _ClassVar[BakCancelBidRequest.BidCancellationType]
        CLASSIC_TYPE: _ClassVar[BakCancelBidRequest.BidCancellationType]
        FRAUD_TYPE: _ClassVar[BakCancelBidRequest.BidCancellationType]
    UNKNOWN_TYPE: BakCancelBidRequest.BidCancellationType
    CLASSIC_TYPE: BakCancelBidRequest.BidCancellationType
    FRAUD_TYPE: BakCancelBidRequest.BidCancellationType
    BID_ID_FIELD_NUMBER: _ClassVar[int]
    BID_CANCELLATION_TYPE_FIELD_NUMBER: _ClassVar[int]
    bid_id: int
    bid_cancellation_type: BakCancelBidRequest.BidCancellationType
    def __init__(self, bid_id: _Optional[int] = ..., bid_cancellation_type: _Optional[_Union[BakCancelBidRequest.BidCancellationType, str]] = ...) -> None: ...

class BakActionRequest(_message.Message):
    __slots__ = ("kamas", "ogrines", "rate", "bid_action")
    KAMAS_FIELD_NUMBER: _ClassVar[int]
    OGRINES_FIELD_NUMBER: _ClassVar[int]
    RATE_FIELD_NUMBER: _ClassVar[int]
    BID_ACTION_FIELD_NUMBER: _ClassVar[int]
    kamas: int
    ogrines: int
    rate: int
    bid_action: BidAction
    def __init__(self, kamas: _Optional[int] = ..., ogrines: _Optional[int] = ..., rate: _Optional[int] = ..., bid_action: _Optional[_Union[BidAction, str]] = ...) -> None: ...

class BakActionEvent(_message.Message):
    __slots__ = ("kamas", "amount", "rate", "bid_action", "transaction_uuid")
    KAMAS_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    RATE_FIELD_NUMBER: _ClassVar[int]
    BID_ACTION_FIELD_NUMBER: _ClassVar[int]
    TRANSACTION_UUID_FIELD_NUMBER: _ClassVar[int]
    kamas: int
    amount: int
    rate: int
    bid_action: BidAction
    transaction_uuid: str
    def __init__(self, kamas: _Optional[int] = ..., amount: _Optional[int] = ..., rate: _Optional[int] = ..., bid_action: _Optional[_Union[BidAction, str]] = ..., transaction_uuid: _Optional[str] = ...) -> None: ...

class BakTransactionValidationRequest(_message.Message):
    __slots__ = ("transaction_uuid",)
    TRANSACTION_UUID_FIELD_NUMBER: _ClassVar[int]
    transaction_uuid: str
    def __init__(self, transaction_uuid: _Optional[str] = ...) -> None: ...

class BakTransactionValidationEvent(_message.Message):
    __slots__ = ("bid_action", "result")
    class BidValidation(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        BID_GENERIC_ERROR: _ClassVar[BakTransactionValidationEvent.BidValidation]
        BID_BUFFER_OVERLOAD: _ClassVar[BakTransactionValidationEvent.BidValidation]
        BID_OFFER_DOESNT_EXIST: _ClassVar[BakTransactionValidationEvent.BidValidation]
        BID_OFFER_ALREADY_EXISTS: _ClassVar[BakTransactionValidationEvent.BidValidation]
        BID_NOT_ENOUGH_KAMAS: _ClassVar[BakTransactionValidationEvent.BidValidation]
        BID_NOT_ENOUGH_OGRINES: _ClassVar[BakTransactionValidationEvent.BidValidation]
        BID_SERVER_MAINTENANCE: _ClassVar[BakTransactionValidationEvent.BidValidation]
        BID_PLAYER_IN_DEBT: _ClassVar[BakTransactionValidationEvent.BidValidation]
        BID_OFFER_IS_YOURS: _ClassVar[BakTransactionValidationEvent.BidValidation]
        BID_VALIDATION_SUCCESS: _ClassVar[BakTransactionValidationEvent.BidValidation]
    BID_GENERIC_ERROR: BakTransactionValidationEvent.BidValidation
    BID_BUFFER_OVERLOAD: BakTransactionValidationEvent.BidValidation
    BID_OFFER_DOESNT_EXIST: BakTransactionValidationEvent.BidValidation
    BID_OFFER_ALREADY_EXISTS: BakTransactionValidationEvent.BidValidation
    BID_NOT_ENOUGH_KAMAS: BakTransactionValidationEvent.BidValidation
    BID_NOT_ENOUGH_OGRINES: BakTransactionValidationEvent.BidValidation
    BID_SERVER_MAINTENANCE: BakTransactionValidationEvent.BidValidation
    BID_PLAYER_IN_DEBT: BakTransactionValidationEvent.BidValidation
    BID_OFFER_IS_YOURS: BakTransactionValidationEvent.BidValidation
    BID_VALIDATION_SUCCESS: BakTransactionValidationEvent.BidValidation
    BID_ACTION_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    bid_action: BidAction
    result: BakTransactionValidationEvent.BidValidation
    def __init__(self, bid_action: _Optional[_Union[BidAction, str]] = ..., result: _Optional[_Union[BakTransactionValidationEvent.BidValidation, str]] = ...) -> None: ...

class BakBuyValidationEvent(_message.Message):
    __slots__ = ("transaction_validation", "amount", "email")
    TRANSACTION_VALIDATION_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    transaction_validation: BakTransactionValidationEvent
    amount: int
    email: str
    def __init__(self, transaction_validation: _Optional[_Union[BakTransactionValidationEvent, _Mapping]] = ..., amount: _Optional[int] = ..., email: _Optional[str] = ...) -> None: ...

class BakApiTokenRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class BakApiKeyEvent(_message.Message):
    __slots__ = ("token",)
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    token: str
    def __init__(self, token: _Optional[str] = ...) -> None: ...

class BakShopTokenRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class BakShopTokenEvent(_message.Message):
    __slots__ = ("token",)
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    token: str
    def __init__(self, token: _Optional[str] = ...) -> None: ...
