import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class BidActivitiesRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class BidActivityResponse(_message.Message):
    __slots__ = ("bid_activities",)
    BID_ACTIVITIES_FIELD_NUMBER: _ClassVar[int]
    bid_activities: _containers.RepeatedCompositeFieldContainer[BidActivity]
    def __init__(self, bid_activities: _Optional[_Iterable[_Union[BidActivity, _Mapping]]] = ...) -> None: ...

class BidActivity(_message.Message):
    __slots__ = ("bidId", "type", "created_at", "object", "price")
    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SELL: _ClassVar[BidActivity.Type]
        BUY: _ClassVar[BidActivity.Type]
        EXPIRE: _ClassVar[BidActivity.Type]
    SELL: BidActivity.Type
    BUY: BidActivity.Type
    EXPIRE: BidActivity.Type
    BIDID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    OBJECT_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    bidId: int
    type: BidActivity.Type
    created_at: str
    object: _common_pb2.ItemMinimalInformation
    price: int
    def __init__(self, bidId: _Optional[int] = ..., type: _Optional[_Union[BidActivity.Type, str]] = ..., created_at: _Optional[str] = ..., object: _Optional[_Union[_common_pb2.ItemMinimalInformation, _Mapping]] = ..., price: _Optional[int] = ...) -> None: ...
