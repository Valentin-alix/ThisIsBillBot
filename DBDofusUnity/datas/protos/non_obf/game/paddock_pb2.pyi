import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PaddockSellRequest(_message.Message):
    __slots__ = ("price", "for_sale")
    PRICE_FIELD_NUMBER: _ClassVar[int]
    FOR_SALE_FIELD_NUMBER: _ClassVar[int]
    price: int
    for_sale: bool
    def __init__(self, price: _Optional[int] = ..., for_sale: bool = ...) -> None: ...

class PaddockBuyRequest(_message.Message):
    __slots__ = ("proposed_price",)
    PROPOSED_PRICE_FIELD_NUMBER: _ClassVar[int]
    proposed_price: int
    def __init__(self, proposed_price: _Optional[int] = ...) -> None: ...

class PaddockRemoveItemRequest(_message.Message):
    __slots__ = ("cell_id",)
    CELL_ID_FIELD_NUMBER: _ClassVar[int]
    cell_id: int
    def __init__(self, cell_id: _Optional[int] = ...) -> None: ...

class PaddockMoveItemRequest(_message.Message):
    __slots__ = ("old_cell_id", "new_cell_id")
    OLD_CELL_ID_FIELD_NUMBER: _ClassVar[int]
    NEW_CELL_ID_FIELD_NUMBER: _ClassVar[int]
    old_cell_id: int
    new_cell_id: int
    def __init__(self, old_cell_id: _Optional[int] = ..., new_cell_id: _Optional[int] = ...) -> None: ...

class PaddocksToSellRequest(_message.Message):
    __slots__ = ("page_index",)
    PAGE_INDEX_FIELD_NUMBER: _ClassVar[int]
    page_index: int
    def __init__(self, page_index: _Optional[int] = ...) -> None: ...

class PaddocksToSellFiltersRequest(_message.Message):
    __slots__ = ("area_id", "at_least_mount_number", "at_least_machine_number", "price_max", "order_by")
    AREA_ID_FIELD_NUMBER: _ClassVar[int]
    AT_LEAST_MOUNT_NUMBER_FIELD_NUMBER: _ClassVar[int]
    AT_LEAST_MACHINE_NUMBER_FIELD_NUMBER: _ClassVar[int]
    PRICE_MAX_FIELD_NUMBER: _ClassVar[int]
    ORDER_BY_FIELD_NUMBER: _ClassVar[int]
    area_id: int
    at_least_mount_number: int
    at_least_machine_number: int
    price_max: int
    order_by: _common_pb2.RealEstateOrder
    def __init__(self, area_id: _Optional[int] = ..., at_least_mount_number: _Optional[int] = ..., at_least_machine_number: _Optional[int] = ..., price_max: _Optional[int] = ..., order_by: _Optional[_Union[_common_pb2.RealEstateOrder, str]] = ...) -> None: ...

class PaddockObjectRemovedEvent(_message.Message):
    __slots__ = ("cell_id",)
    CELL_ID_FIELD_NUMBER: _ClassVar[int]
    cell_id: int
    def __init__(self, cell_id: _Optional[int] = ...) -> None: ...

class PaddockObjectAddedEvent(_message.Message):
    __slots__ = ("paddock_item",)
    PADDOCK_ITEM_FIELD_NUMBER: _ClassVar[int]
    paddock_item: _common_pb2.ObjectInRolePlay
    def __init__(self, paddock_item: _Optional[_Union[_common_pb2.ObjectInRolePlay, _Mapping]] = ...) -> None: ...

class PaddockObjectsAddedEvent(_message.Message):
    __slots__ = ("paddock_item",)
    PADDOCK_ITEM_FIELD_NUMBER: _ClassVar[int]
    paddock_item: _containers.RepeatedCompositeFieldContainer[_common_pb2.ObjectInRolePlay]
    def __init__(self, paddock_item: _Optional[_Iterable[_Union[_common_pb2.ObjectInRolePlay, _Mapping]]] = ...) -> None: ...

class PaddockBuyResultEvent(_message.Message):
    __slots__ = ("paddock_id", "bought", "price")
    PADDOCK_ID_FIELD_NUMBER: _ClassVar[int]
    BOUGHT_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    paddock_id: int
    bought: bool
    price: int
    def __init__(self, paddock_id: _Optional[int] = ..., bought: bool = ..., price: _Optional[int] = ...) -> None: ...

class PaddockPropertiesEvent(_message.Message):
    __slots__ = ("properties",)
    PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    properties: _common_pb2.PaddockInformation
    def __init__(self, properties: _Optional[_Union[_common_pb2.PaddockInformation, _Mapping]] = ...) -> None: ...

class PaddockTransactionDialogEvent(_message.Message):
    __slots__ = ("transaction", "owner_id", "price")
    class Transaction(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        BUY: _ClassVar[PaddockTransactionDialogEvent.Transaction]
        SELL: _ClassVar[PaddockTransactionDialogEvent.Transaction]
    BUY: PaddockTransactionDialogEvent.Transaction
    SELL: PaddockTransactionDialogEvent.Transaction
    TRANSACTION_FIELD_NUMBER: _ClassVar[int]
    OWNER_ID_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    transaction: PaddockTransactionDialogEvent.Transaction
    owner_id: int
    price: int
    def __init__(self, transaction: _Optional[_Union[PaddockTransactionDialogEvent.Transaction, str]] = ..., owner_id: _Optional[int] = ..., price: _Optional[int] = ...) -> None: ...

class PaddockObjectAnimationPlayEvent(_message.Message):
    __slots__ = ("cells_id",)
    CELLS_ID_FIELD_NUMBER: _ClassVar[int]
    cells_id: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, cells_id: _Optional[_Iterable[int]] = ...) -> None: ...

class PaddocksToSellEvent(_message.Message):
    __slots__ = ("page_index", "page_total", "paddocks")
    class PaddockForSale(_message.Message):
        __slots__ = ("guild_owner", "coordinates", "sub_area_id", "mount_number", "object_number", "price")
        GUILD_OWNER_FIELD_NUMBER: _ClassVar[int]
        COORDINATES_FIELD_NUMBER: _ClassVar[int]
        SUB_AREA_ID_FIELD_NUMBER: _ClassVar[int]
        MOUNT_NUMBER_FIELD_NUMBER: _ClassVar[int]
        OBJECT_NUMBER_FIELD_NUMBER: _ClassVar[int]
        PRICE_FIELD_NUMBER: _ClassVar[int]
        guild_owner: str
        coordinates: _common_pb2.MapCoordinates
        sub_area_id: int
        mount_number: int
        object_number: int
        price: int
        def __init__(self, guild_owner: _Optional[str] = ..., coordinates: _Optional[_Union[_common_pb2.MapCoordinates, _Mapping]] = ..., sub_area_id: _Optional[int] = ..., mount_number: _Optional[int] = ..., object_number: _Optional[int] = ..., price: _Optional[int] = ...) -> None: ...
    PAGE_INDEX_FIELD_NUMBER: _ClassVar[int]
    PAGE_TOTAL_FIELD_NUMBER: _ClassVar[int]
    PADDOCKS_FIELD_NUMBER: _ClassVar[int]
    page_index: int
    page_total: int
    paddocks: _containers.RepeatedCompositeFieldContainer[PaddocksToSellEvent.PaddockForSale]
    def __init__(self, page_index: _Optional[int] = ..., page_total: _Optional[int] = ..., paddocks: _Optional[_Iterable[_Union[PaddocksToSellEvent.PaddockForSale, _Mapping]]] = ...) -> None: ...
