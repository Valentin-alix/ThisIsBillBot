from com.ankama.dofus.server.game.protocol import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ExchangeObjectMoveRequest(_message.Message):
    __slots__ = ("object_uid", "quantity")
    OBJECT_UID_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    object_uid: int
    quantity: int
    def __init__(self, object_uid: _Optional[int] = ..., quantity: _Optional[int] = ...) -> None: ...

class ExchangeSetCraftRecipeRequest(_message.Message):
    __slots__ = ("object_uid",)
    OBJECT_UID_FIELD_NUMBER: _ClassVar[int]
    object_uid: int
    def __init__(self, object_uid: _Optional[int] = ...) -> None: ...

class ExchangeObjectUseInWorkshopRequest(_message.Message):
    __slots__ = ("object_uid", "quantity")
    OBJECT_UID_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    object_uid: int
    quantity: int
    def __init__(self, object_uid: _Optional[int] = ..., quantity: _Optional[int] = ...) -> None: ...

class ExchangeObjectMoveToTabRequest(_message.Message):
    __slots__ = ("object_uid", "quantity", "tab_number")
    OBJECT_UID_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    TAB_NUMBER_FIELD_NUMBER: _ClassVar[int]
    object_uid: int
    quantity: int
    tab_number: int
    def __init__(self, object_uid: _Optional[int] = ..., quantity: _Optional[int] = ..., tab_number: _Optional[int] = ...) -> None: ...

class ExchangeObjectMovePricedRequest(_message.Message):
    __slots__ = ("object_uid", "quantity", "price")
    OBJECT_UID_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    object_uid: int
    quantity: int
    price: int
    def __init__(self, object_uid: _Optional[int] = ..., quantity: _Optional[int] = ..., price: _Optional[int] = ...) -> None: ...

class ExchangeObjectModifyPricedRequest(_message.Message):
    __slots__ = ("object_uid", "quantity", "price")
    OBJECT_UID_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    object_uid: int
    quantity: int
    price: int
    def __init__(self, object_uid: _Optional[int] = ..., quantity: _Optional[int] = ..., price: _Optional[int] = ...) -> None: ...

class ExchangeObjectTransferAllToInventoryRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ExchangeObjectTransferListToInventoryRequest(_message.Message):
    __slots__ = ("objects_uid",)
    OBJECTS_UID_FIELD_NUMBER: _ClassVar[int]
    objects_uid: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, objects_uid: _Optional[_Iterable[int]] = ...) -> None: ...

class ExchangeObjectTransferListWithQuantityToInventoryRequest(_message.Message):
    __slots__ = ("objects",)
    OBJECTS_FIELD_NUMBER: _ClassVar[int]
    objects: _containers.RepeatedCompositeFieldContainer[_common_pb2.ObjectUidWithQuantity]
    def __init__(self, objects: _Optional[_Iterable[_Union[_common_pb2.ObjectUidWithQuantity, _Mapping]]] = ...) -> None: ...

class ExchangeObjectTransferExistingToInventoryRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ExchangeObjectTransferAllFromInventoryRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ExchangeObjectTransferListFromInventoryRequest(_message.Message):
    __slots__ = ("objects_uid",)
    OBJECTS_UID_FIELD_NUMBER: _ClassVar[int]
    objects_uid: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, objects_uid: _Optional[_Iterable[int]] = ...) -> None: ...

class ExchangeObjectTransferTypeFromInventoryRequest(_message.Message):
    __slots__ = ("object_type",)
    OBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    object_type: int
    def __init__(self, object_type: _Optional[int] = ...) -> None: ...

class ExchangeObjectTransferExistingFromInventoryRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ExchangeMoveKamaRequest(_message.Message):
    __slots__ = ("quantity",)
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    quantity: int
    def __init__(self, quantity: _Optional[int] = ...) -> None: ...

class ExchangeCraftCountRequest(_message.Message):
    __slots__ = ("count",)
    COUNT_FIELD_NUMBER: _ClassVar[int]
    count: int
    def __init__(self, count: _Optional[int] = ...) -> None: ...

class ExchangeReplayStopRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ExchangeMultiCraftSetCrafterCanUseHisResourcesRequest(_message.Message):
    __slots__ = ("allow",)
    ALLOW_FIELD_NUMBER: _ClassVar[int]
    allow: bool
    def __init__(self, allow: bool = ...) -> None: ...

class ExchangePlayerRequest(_message.Message):
    __slots__ = ("target_id",)
    TARGET_ID_FIELD_NUMBER: _ClassVar[int]
    target_id: int
    def __init__(self, target_id: _Optional[int] = ...) -> None: ...

class ExchangePlayerMultiCraftRequest(_message.Message):
    __slots__ = ("exchange_type", "target_id", "skill_id")
    EXCHANGE_TYPE_FIELD_NUMBER: _ClassVar[int]
    TARGET_ID_FIELD_NUMBER: _ClassVar[int]
    SKILL_ID_FIELD_NUMBER: _ClassVar[int]
    exchange_type: _common_pb2.ExchangeType
    target_id: int
    skill_id: int
    def __init__(self, exchange_type: _Optional[_Union[_common_pb2.ExchangeType, str]] = ..., target_id: _Optional[int] = ..., skill_id: _Optional[int] = ...) -> None: ...

class ExchangeMountRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ExchangeTaxCollectorRequest(_message.Message):
    __slots__ = ("tax_collector_uuid",)
    TAX_COLLECTOR_UUID_FIELD_NUMBER: _ClassVar[int]
    tax_collector_uuid: str
    def __init__(self, tax_collector_uuid: _Optional[str] = ...) -> None: ...

class ExchangeAcceptRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ExchangeReadyRequest(_message.Message):
    __slots__ = ("ready", "step")
    READY_FIELD_NUMBER: _ClassVar[int]
    STEP_FIELD_NUMBER: _ClassVar[int]
    ready: bool
    step: int
    def __init__(self, ready: bool = ..., step: _Optional[int] = ...) -> None: ...

class ExchangeFocusedReadyRequest(_message.Message):
    __slots__ = ("ready", "step", "focus_action_id")
    READY_FIELD_NUMBER: _ClassVar[int]
    STEP_FIELD_NUMBER: _ClassVar[int]
    FOCUS_ACTION_ID_FIELD_NUMBER: _ClassVar[int]
    ready: bool
    step: int
    focus_action_id: int
    def __init__(self, ready: bool = ..., step: _Optional[int] = ..., focus_action_id: _Optional[int] = ...) -> None: ...

class ExchangeCraftPaymentModificationRequest(_message.Message):
    __slots__ = ("quantity",)
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    quantity: int
    def __init__(self, quantity: _Optional[int] = ...) -> None: ...

class ExchangeBuyRequest(_message.Message):
    __slots__ = ("object_uid", "quantity")
    OBJECT_UID_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    object_uid: int
    quantity: int
    def __init__(self, object_uid: _Optional[int] = ..., quantity: _Optional[int] = ...) -> None: ...

class ExchangeSellRequest(_message.Message):
    __slots__ = ("object_uid", "quantity")
    OBJECT_UID_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    object_uid: int
    quantity: int
    def __init__(self, object_uid: _Optional[int] = ..., quantity: _Optional[int] = ...) -> None: ...

class ExchangeObjectsSellRequest(_message.Message):
    __slots__ = ("objects",)
    class ExchangeObject(_message.Message):
        __slots__ = ("object_uid", "quantity")
        OBJECT_UID_FIELD_NUMBER: _ClassVar[int]
        QUANTITY_FIELD_NUMBER: _ClassVar[int]
        object_uid: int
        quantity: int
        def __init__(self, object_uid: _Optional[int] = ..., quantity: _Optional[int] = ...) -> None: ...
    OBJECTS_FIELD_NUMBER: _ClassVar[int]
    objects: _containers.RepeatedCompositeFieldContainer[ExchangeObjectsSellRequest.ExchangeObject]
    def __init__(self, objects: _Optional[_Iterable[_Union[ExchangeObjectsSellRequest.ExchangeObject, _Mapping]]] = ...) -> None: ...

class JobBookSubscribeRequest(_message.Message):
    __slots__ = ("jobs_id",)
    JOBS_ID_FIELD_NUMBER: _ClassVar[int]
    jobs_id: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, jobs_id: _Optional[_Iterable[int]] = ...) -> None: ...

class ExchangeHandleMountsRequest(_message.Message):
    __slots__ = ("action_type", "rides_id")
    class ExchangeHandleMountStableType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        EXCHANGE_MOUNT_STABLES_PUT: _ClassVar[ExchangeHandleMountsRequest.ExchangeHandleMountStableType]
        EXCHANGE_MOUNT_STABLES_GET: _ClassVar[ExchangeHandleMountsRequest.ExchangeHandleMountStableType]
        EXCHANGE_MOUNT_STABLES_FREE: _ClassVar[ExchangeHandleMountsRequest.ExchangeHandleMountStableType]
        EXCHANGE_MOUNT_STABLES_CERTIF: _ClassVar[ExchangeHandleMountsRequest.ExchangeHandleMountStableType]
        EXCHANGE_MOUNT_STABLES_UNCERTIF: _ClassVar[ExchangeHandleMountsRequest.ExchangeHandleMountStableType]
        EXCHANGE_MOUNT_PADDOCK_PUT: _ClassVar[ExchangeHandleMountsRequest.ExchangeHandleMountStableType]
        EXCHANGE_MOUNT_PADDOCK_GET: _ClassVar[ExchangeHandleMountsRequest.ExchangeHandleMountStableType]
        EXCHANGE_MOUNT_PADDOCK_FREE: _ClassVar[ExchangeHandleMountsRequest.ExchangeHandleMountStableType]
        EXCHANGE_EQUIPPED_MOUNT_PADDOCK_PUT: _ClassVar[ExchangeHandleMountsRequest.ExchangeHandleMountStableType]
        EXCHANGE_EQUIPPED_MOUNT_PADDOCK_GET: _ClassVar[ExchangeHandleMountsRequest.ExchangeHandleMountStableType]
        EXCHANGE_EQUIPPED_FREE: _ClassVar[ExchangeHandleMountsRequest.ExchangeHandleMountStableType]
        EXCHANGE_CERTIFICATE_FREE: _ClassVar[ExchangeHandleMountsRequest.ExchangeHandleMountStableType]
        EXCHANGE_EQUIPPED_CERTIF: _ClassVar[ExchangeHandleMountsRequest.ExchangeHandleMountStableType]
        EXCHANGE_MOUNT_PADDOCK_CERTIF: _ClassVar[ExchangeHandleMountsRequest.ExchangeHandleMountStableType]
        EXCHANGE_UNCERTIF_TO_EQUIPPED: _ClassVar[ExchangeHandleMountsRequest.ExchangeHandleMountStableType]
        EXCHANGE_UNCERTIF_TO_PADDOCK: _ClassVar[ExchangeHandleMountsRequest.ExchangeHandleMountStableType]
        EXCHANGE_MOUNT_STABLES_STERILIZE: _ClassVar[ExchangeHandleMountsRequest.ExchangeHandleMountStableType]
        EXCHANGE_EQUIPPED_STERILIZE: _ClassVar[ExchangeHandleMountsRequest.ExchangeHandleMountStableType]
        EXCHANGE_MOUNT_PADDOCK_STERILIZE: _ClassVar[ExchangeHandleMountsRequest.ExchangeHandleMountStableType]
    EXCHANGE_MOUNT_STABLES_PUT: ExchangeHandleMountsRequest.ExchangeHandleMountStableType
    EXCHANGE_MOUNT_STABLES_GET: ExchangeHandleMountsRequest.ExchangeHandleMountStableType
    EXCHANGE_MOUNT_STABLES_FREE: ExchangeHandleMountsRequest.ExchangeHandleMountStableType
    EXCHANGE_MOUNT_STABLES_CERTIF: ExchangeHandleMountsRequest.ExchangeHandleMountStableType
    EXCHANGE_MOUNT_STABLES_UNCERTIF: ExchangeHandleMountsRequest.ExchangeHandleMountStableType
    EXCHANGE_MOUNT_PADDOCK_PUT: ExchangeHandleMountsRequest.ExchangeHandleMountStableType
    EXCHANGE_MOUNT_PADDOCK_GET: ExchangeHandleMountsRequest.ExchangeHandleMountStableType
    EXCHANGE_MOUNT_PADDOCK_FREE: ExchangeHandleMountsRequest.ExchangeHandleMountStableType
    EXCHANGE_EQUIPPED_MOUNT_PADDOCK_PUT: ExchangeHandleMountsRequest.ExchangeHandleMountStableType
    EXCHANGE_EQUIPPED_MOUNT_PADDOCK_GET: ExchangeHandleMountsRequest.ExchangeHandleMountStableType
    EXCHANGE_EQUIPPED_FREE: ExchangeHandleMountsRequest.ExchangeHandleMountStableType
    EXCHANGE_CERTIFICATE_FREE: ExchangeHandleMountsRequest.ExchangeHandleMountStableType
    EXCHANGE_EQUIPPED_CERTIF: ExchangeHandleMountsRequest.ExchangeHandleMountStableType
    EXCHANGE_MOUNT_PADDOCK_CERTIF: ExchangeHandleMountsRequest.ExchangeHandleMountStableType
    EXCHANGE_UNCERTIF_TO_EQUIPPED: ExchangeHandleMountsRequest.ExchangeHandleMountStableType
    EXCHANGE_UNCERTIF_TO_PADDOCK: ExchangeHandleMountsRequest.ExchangeHandleMountStableType
    EXCHANGE_MOUNT_STABLES_STERILIZE: ExchangeHandleMountsRequest.ExchangeHandleMountStableType
    EXCHANGE_EQUIPPED_STERILIZE: ExchangeHandleMountsRequest.ExchangeHandleMountStableType
    EXCHANGE_MOUNT_PADDOCK_STERILIZE: ExchangeHandleMountsRequest.ExchangeHandleMountStableType
    ACTION_TYPE_FIELD_NUMBER: _ClassVar[int]
    RIDES_ID_FIELD_NUMBER: _ClassVar[int]
    action_type: ExchangeHandleMountsRequest.ExchangeHandleMountStableType
    rides_id: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, action_type: _Optional[_Union[ExchangeHandleMountsRequest.ExchangeHandleMountStableType, str]] = ..., rides_id: _Optional[_Iterable[int]] = ...) -> None: ...

class ExchangeBidHouseSearchRequest(_message.Message):
    __slots__ = ("object_gid", "follow")
    OBJECT_GID_FIELD_NUMBER: _ClassVar[int]
    FOLLOW_FIELD_NUMBER: _ClassVar[int]
    object_gid: int
    follow: bool
    def __init__(self, object_gid: _Optional[int] = ..., follow: bool = ...) -> None: ...

class ExchangeBidHouseListRequest(_message.Message):
    __slots__ = ("object_gid", "follow")
    OBJECT_GID_FIELD_NUMBER: _ClassVar[int]
    FOLLOW_FIELD_NUMBER: _ClassVar[int]
    object_gid: int
    follow: bool
    def __init__(self, object_gid: _Optional[int] = ..., follow: bool = ...) -> None: ...

class ExchangeBidHouseTypeRequest(_message.Message):
    __slots__ = ("type_id", "follow")
    TYPE_ID_FIELD_NUMBER: _ClassVar[int]
    FOLLOW_FIELD_NUMBER: _ClassVar[int]
    type_id: int
    follow: bool
    def __init__(self, type_id: _Optional[int] = ..., follow: bool = ...) -> None: ...

class ExchangeBidHouseBuyRequest(_message.Message):
    __slots__ = ("bid_item_uid", "quantity", "price")
    BID_ITEM_UID_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    bid_item_uid: int
    quantity: int
    price: int
    def __init__(self, bid_item_uid: _Optional[int] = ..., quantity: _Optional[int] = ..., price: _Optional[int] = ...) -> None: ...

class ExchangeBidHousePriceRequest(_message.Message):
    __slots__ = ("object_gid",)
    OBJECT_GID_FIELD_NUMBER: _ClassVar[int]
    object_gid: int
    def __init__(self, object_gid: _Optional[int] = ...) -> None: ...

class ExchangeTaxCollectorEquipmentRequest(_message.Message):
    __slots__ = ("tax_collector_uid",)
    TAX_COLLECTOR_UID_FIELD_NUMBER: _ClassVar[int]
    tax_collector_uid: str
    def __init__(self, tax_collector_uid: _Optional[str] = ...) -> None: ...

class ObjectAveragePricesRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ExchangeMoneyMovementLimitEvent(_message.Message):
    __slots__ = ("limit",)
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    limit: int
    def __init__(self, limit: _Optional[int] = ...) -> None: ...

class ExchangeCraftCountModifiedEvent(_message.Message):
    __slots__ = ("count",)
    COUNT_FIELD_NUMBER: _ClassVar[int]
    count: int
    def __init__(self, count: _Optional[int] = ...) -> None: ...

class ExchangeObjectsAddedEvent(_message.Message):
    __slots__ = ("remote", "objects", "fm_power")
    REMOTE_FIELD_NUMBER: _ClassVar[int]
    OBJECTS_FIELD_NUMBER: _ClassVar[int]
    FM_POWER_FIELD_NUMBER: _ClassVar[int]
    remote: bool
    objects: _containers.RepeatedCompositeFieldContainer[_common_pb2.ObjectItemInventory]
    fm_power: float
    def __init__(self, remote: bool = ..., objects: _Optional[_Iterable[_Union[_common_pb2.ObjectItemInventory, _Mapping]]] = ..., fm_power: _Optional[float] = ...) -> None: ...

class ExchangeObjectRemovedEvent(_message.Message):
    __slots__ = ("remote", "bid_item_uid")
    REMOTE_FIELD_NUMBER: _ClassVar[int]
    BID_ITEM_UID_FIELD_NUMBER: _ClassVar[int]
    remote: bool
    bid_item_uid: int
    def __init__(self, remote: bool = ..., bid_item_uid: _Optional[int] = ...) -> None: ...

class ExchangeObjectsRemovedEvent(_message.Message):
    __slots__ = ("remote", "bid_items_uid")
    REMOTE_FIELD_NUMBER: _ClassVar[int]
    BID_ITEMS_UID_FIELD_NUMBER: _ClassVar[int]
    remote: bool
    bid_items_uid: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, remote: bool = ..., bid_items_uid: _Optional[_Iterable[int]] = ...) -> None: ...

class ExchangeObjectsModifiedEvent(_message.Message):
    __slots__ = ("remote", "objects")
    REMOTE_FIELD_NUMBER: _ClassVar[int]
    OBJECTS_FIELD_NUMBER: _ClassVar[int]
    remote: bool
    objects: _containers.RepeatedCompositeFieldContainer[_common_pb2.ObjectItemInventory]
    def __init__(self, remote: bool = ..., objects: _Optional[_Iterable[_Union[_common_pb2.ObjectItemInventory, _Mapping]]] = ...) -> None: ...

class ExchangeObjectPutInBagEvent(_message.Message):
    __slots__ = ("remote", "object")
    REMOTE_FIELD_NUMBER: _ClassVar[int]
    OBJECT_FIELD_NUMBER: _ClassVar[int]
    remote: bool
    object: _common_pb2.ObjectItemInventory
    def __init__(self, remote: bool = ..., object: _Optional[_Union[_common_pb2.ObjectItemInventory, _Mapping]] = ...) -> None: ...

class ExchangeObjectRemovedFromBagEvent(_message.Message):
    __slots__ = ("remote", "object_uid")
    REMOTE_FIELD_NUMBER: _ClassVar[int]
    OBJECT_UID_FIELD_NUMBER: _ClassVar[int]
    remote: bool
    object_uid: int
    def __init__(self, remote: bool = ..., object_uid: _Optional[int] = ...) -> None: ...

class ExchangeObjectModifiedInBagEvent(_message.Message):
    __slots__ = ("remote", "object")
    REMOTE_FIELD_NUMBER: _ClassVar[int]
    OBJECT_FIELD_NUMBER: _ClassVar[int]
    remote: bool
    object: _common_pb2.ObjectItemInventory
    def __init__(self, remote: bool = ..., object: _Optional[_Union[_common_pb2.ObjectItemInventory, _Mapping]] = ...) -> None: ...

class ExchangeKamaModifiedEvent(_message.Message):
    __slots__ = ("remote", "quantity")
    REMOTE_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    remote: bool
    quantity: int
    def __init__(self, remote: bool = ..., quantity: _Optional[int] = ...) -> None: ...

class ExchangePodsModifiedEvent(_message.Message):
    __slots__ = ("remote", "current_weight", "max_weight")
    REMOTE_FIELD_NUMBER: _ClassVar[int]
    CURRENT_WEIGHT_FIELD_NUMBER: _ClassVar[int]
    MAX_WEIGHT_FIELD_NUMBER: _ClassVar[int]
    remote: bool
    current_weight: int
    max_weight: int
    def __init__(self, remote: bool = ..., current_weight: _Optional[int] = ..., max_weight: _Optional[int] = ...) -> None: ...

class ExchangeMultiCraftCrafterCanUseHisResourcesEvent(_message.Message):
    __slots__ = ("allowed",)
    ALLOWED_FIELD_NUMBER: _ClassVar[int]
    allowed: bool
    def __init__(self, allowed: bool = ...) -> None: ...

class ExchangeRequestedTradeEvent(_message.Message):
    __slots__ = ("exchange_type", "source_id", "target_id")
    EXCHANGE_TYPE_FIELD_NUMBER: _ClassVar[int]
    SOURCE_ID_FIELD_NUMBER: _ClassVar[int]
    TARGET_ID_FIELD_NUMBER: _ClassVar[int]
    exchange_type: _common_pb2.ExchangeType
    source_id: int
    target_id: int
    def __init__(self, exchange_type: _Optional[_Union[_common_pb2.ExchangeType, str]] = ..., source_id: _Optional[int] = ..., target_id: _Optional[int] = ...) -> None: ...

class ExchangeStartedEvent(_message.Message):
    __slots__ = ("exchange_type",)
    EXCHANGE_TYPE_FIELD_NUMBER: _ClassVar[int]
    exchange_type: _common_pb2.ExchangeType
    def __init__(self, exchange_type: _Optional[_Union[_common_pb2.ExchangeType, str]] = ...) -> None: ...

class ExchangeStartedWithPodsEvent(_message.Message):
    __slots__ = ("exchange_type", "first_character_id", "first_character_current_weight", "first_character_max_weight", "second_character_id", "second_character_current_weight", "second_character_max_weight")
    EXCHANGE_TYPE_FIELD_NUMBER: _ClassVar[int]
    FIRST_CHARACTER_ID_FIELD_NUMBER: _ClassVar[int]
    FIRST_CHARACTER_CURRENT_WEIGHT_FIELD_NUMBER: _ClassVar[int]
    FIRST_CHARACTER_MAX_WEIGHT_FIELD_NUMBER: _ClassVar[int]
    SECOND_CHARACTER_ID_FIELD_NUMBER: _ClassVar[int]
    SECOND_CHARACTER_CURRENT_WEIGHT_FIELD_NUMBER: _ClassVar[int]
    SECOND_CHARACTER_MAX_WEIGHT_FIELD_NUMBER: _ClassVar[int]
    exchange_type: _common_pb2.ExchangeType
    first_character_id: int
    first_character_current_weight: int
    first_character_max_weight: int
    second_character_id: int
    second_character_current_weight: int
    second_character_max_weight: int
    def __init__(self, exchange_type: _Optional[_Union[_common_pb2.ExchangeType, str]] = ..., first_character_id: _Optional[int] = ..., first_character_current_weight: _Optional[int] = ..., first_character_max_weight: _Optional[int] = ..., second_character_id: _Optional[int] = ..., second_character_current_weight: _Optional[int] = ..., second_character_max_weight: _Optional[int] = ...) -> None: ...

class ExchangeStartedWithStorageEvent(_message.Message):
    __slots__ = ("exchange_type", "storage_max_slot")
    EXCHANGE_TYPE_FIELD_NUMBER: _ClassVar[int]
    STORAGE_MAX_SLOT_FIELD_NUMBER: _ClassVar[int]
    exchange_type: _common_pb2.ExchangeType
    storage_max_slot: int
    def __init__(self, exchange_type: _Optional[_Union[_common_pb2.ExchangeType, str]] = ..., storage_max_slot: _Optional[int] = ...) -> None: ...

class ExchangeStartedWithMultiTabStorageEvent(_message.Message):
    __slots__ = ("exchange_type", "storage_max_slot", "tab_number")
    EXCHANGE_TYPE_FIELD_NUMBER: _ClassVar[int]
    STORAGE_MAX_SLOT_FIELD_NUMBER: _ClassVar[int]
    TAB_NUMBER_FIELD_NUMBER: _ClassVar[int]
    exchange_type: _common_pb2.ExchangeType
    storage_max_slot: int
    tab_number: int
    def __init__(self, exchange_type: _Optional[_Union[_common_pb2.ExchangeType, str]] = ..., storage_max_slot: _Optional[int] = ..., tab_number: _Optional[int] = ...) -> None: ...

class ExchangeBidHouseBuyResultEvent(_message.Message):
    __slots__ = ("bid_item_uid", "bought")
    BID_ITEM_UID_FIELD_NUMBER: _ClassVar[int]
    BOUGHT_FIELD_NUMBER: _ClassVar[int]
    bid_item_uid: int
    bought: bool
    def __init__(self, bid_item_uid: _Optional[int] = ..., bought: bool = ...) -> None: ...

class ExchangeBidHouseItemAddedEvent(_message.Message):
    __slots__ = ("item", "price", "unsold_delay")
    ITEM_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    UNSOLD_DELAY_FIELD_NUMBER: _ClassVar[int]
    item: BidItem
    price: int
    unsold_delay: int
    def __init__(self, item: _Optional[_Union[BidItem, _Mapping]] = ..., price: _Optional[int] = ..., unsold_delay: _Optional[int] = ...) -> None: ...

class ExchangeBidHouseItemRemovedEvent(_message.Message):
    __slots__ = ("sell_id",)
    SELL_ID_FIELD_NUMBER: _ClassVar[int]
    sell_id: int
    def __init__(self, sell_id: _Optional[int] = ...) -> None: ...

class ExchangeBidHouseGenericItemAddedEvent(_message.Message):
    __slots__ = ("object_gid",)
    OBJECT_GID_FIELD_NUMBER: _ClassVar[int]
    object_gid: int
    def __init__(self, object_gid: _Optional[int] = ...) -> None: ...

class ExchangeBidHouseGenericItemRemovedEvent(_message.Message):
    __slots__ = ("object_gid",)
    OBJECT_GID_FIELD_NUMBER: _ClassVar[int]
    object_gid: int
    def __init__(self, object_gid: _Optional[int] = ...) -> None: ...

class ExchangeBidHouseInListAddedEvent(_message.Message):
    __slots__ = ("bid_item_uid", "object_gid", "object_type", "effects", "prices")
    BID_ITEM_UID_FIELD_NUMBER: _ClassVar[int]
    OBJECT_GID_FIELD_NUMBER: _ClassVar[int]
    OBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    EFFECTS_FIELD_NUMBER: _ClassVar[int]
    PRICES_FIELD_NUMBER: _ClassVar[int]
    bid_item_uid: int
    object_gid: int
    object_type: int
    effects: _containers.RepeatedCompositeFieldContainer[_common_pb2.ObjectEffect]
    prices: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, bid_item_uid: _Optional[int] = ..., object_gid: _Optional[int] = ..., object_type: _Optional[int] = ..., effects: _Optional[_Iterable[_Union[_common_pb2.ObjectEffect, _Mapping]]] = ..., prices: _Optional[_Iterable[int]] = ...) -> None: ...

class ExchangeBidHouseInListUpdatedEvent(_message.Message):
    __slots__ = ("bid_item_uid", "object_gid", "object_type", "effects", "prices")
    BID_ITEM_UID_FIELD_NUMBER: _ClassVar[int]
    OBJECT_GID_FIELD_NUMBER: _ClassVar[int]
    OBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    EFFECTS_FIELD_NUMBER: _ClassVar[int]
    PRICES_FIELD_NUMBER: _ClassVar[int]
    bid_item_uid: int
    object_gid: int
    object_type: int
    effects: _containers.RepeatedCompositeFieldContainer[_common_pb2.ObjectEffect]
    prices: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, bid_item_uid: _Optional[int] = ..., object_gid: _Optional[int] = ..., object_type: _Optional[int] = ..., effects: _Optional[_Iterable[_Union[_common_pb2.ObjectEffect, _Mapping]]] = ..., prices: _Optional[_Iterable[int]] = ...) -> None: ...

class ExchangeBidHouseInListRemovedEvent(_message.Message):
    __slots__ = ("bid_item_uid", "object_gid", "object_type")
    BID_ITEM_UID_FIELD_NUMBER: _ClassVar[int]
    OBJECT_GID_FIELD_NUMBER: _ClassVar[int]
    OBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    bid_item_uid: int
    object_gid: int
    object_type: int
    def __init__(self, bid_item_uid: _Optional[int] = ..., object_gid: _Optional[int] = ..., object_type: _Optional[int] = ...) -> None: ...

class ExchangeBidHouseUnsoldItemsEvent(_message.Message):
    __slots__ = ("objects",)
    OBJECTS_FIELD_NUMBER: _ClassVar[int]
    objects: _containers.RepeatedCompositeFieldContainer[_common_pb2.ObjectGidWithQuantity]
    def __init__(self, objects: _Optional[_Iterable[_Union[_common_pb2.ObjectGidWithQuantity, _Mapping]]] = ...) -> None: ...

class ExchangeBidHouseOfflineSoldItemsEvent(_message.Message):
    __slots__ = ("bid_house_items",)
    BID_HOUSE_ITEMS_FIELD_NUMBER: _ClassVar[int]
    bid_house_items: _containers.RepeatedCompositeFieldContainer[_common_pb2.ObjectGidWithQuantity]
    def __init__(self, bid_house_items: _Optional[_Iterable[_Union[_common_pb2.ObjectGidWithQuantity, _Mapping]]] = ...) -> None: ...

class ExchangeReadyEvent(_message.Message):
    __slots__ = ("character_id", "ready")
    CHARACTER_ID_FIELD_NUMBER: _ClassVar[int]
    READY_FIELD_NUMBER: _ClassVar[int]
    character_id: int
    ready: bool
    def __init__(self, character_id: _Optional[int] = ..., ready: bool = ...) -> None: ...

class ExchangeStoppedEvent(_message.Message):
    __slots__ = ("character_id",)
    CHARACTER_ID_FIELD_NUMBER: _ClassVar[int]
    character_id: int
    def __init__(self, character_id: _Optional[int] = ...) -> None: ...

class ExchangeErrorEvent(_message.Message):
    __slots__ = ("error_type",)
    class ExchangeError(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        REQUEST_IMPOSSIBLE: _ClassVar[ExchangeErrorEvent.ExchangeError]
        REQUEST_CHARACTER_OCCUPIED: _ClassVar[ExchangeErrorEvent.ExchangeError]
        REQUEST_CHARACTER_JOB_NOT_EQUIPPED: _ClassVar[ExchangeErrorEvent.ExchangeError]
        REQUEST_CHARACTER_TOOL_TOO_FAR: _ClassVar[ExchangeErrorEvent.ExchangeError]
        REQUEST_CHARACTER_OVERLOADED: _ClassVar[ExchangeErrorEvent.ExchangeError]
        REQUEST_CHARACTER_NOT_SUBSCRIBER: _ClassVar[ExchangeErrorEvent.ExchangeError]
        REQUEST_CHARACTER_GUEST: _ClassVar[ExchangeErrorEvent.ExchangeError]
        MOUNT_PADDOCK_ERROR: _ClassVar[ExchangeErrorEvent.ExchangeError]
        BID_SEARCH_ERROR: _ClassVar[ExchangeErrorEvent.ExchangeError]
        SELL_ERROR: _ClassVar[ExchangeErrorEvent.ExchangeError]
        BUY_ERROR: _ClassVar[ExchangeErrorEvent.ExchangeError]
    REQUEST_IMPOSSIBLE: ExchangeErrorEvent.ExchangeError
    REQUEST_CHARACTER_OCCUPIED: ExchangeErrorEvent.ExchangeError
    REQUEST_CHARACTER_JOB_NOT_EQUIPPED: ExchangeErrorEvent.ExchangeError
    REQUEST_CHARACTER_TOOL_TOO_FAR: ExchangeErrorEvent.ExchangeError
    REQUEST_CHARACTER_OVERLOADED: ExchangeErrorEvent.ExchangeError
    REQUEST_CHARACTER_NOT_SUBSCRIBER: ExchangeErrorEvent.ExchangeError
    REQUEST_CHARACTER_GUEST: ExchangeErrorEvent.ExchangeError
    MOUNT_PADDOCK_ERROR: ExchangeErrorEvent.ExchangeError
    BID_SEARCH_ERROR: ExchangeErrorEvent.ExchangeError
    SELL_ERROR: ExchangeErrorEvent.ExchangeError
    BUY_ERROR: ExchangeErrorEvent.ExchangeError
    ERROR_TYPE_FIELD_NUMBER: _ClassVar[int]
    error_type: ExchangeErrorEvent.ExchangeError
    def __init__(self, error_type: _Optional[_Union[ExchangeErrorEvent.ExchangeError, str]] = ...) -> None: ...

class ExchangeLeaveEvent(_message.Message):
    __slots__ = ("dialog_type", "success")
    DIALOG_TYPE_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    dialog_type: _common_pb2.DialogType
    success: bool
    def __init__(self, dialog_type: _Optional[_Union[_common_pb2.DialogType, str]] = ..., success: bool = ...) -> None: ...

class ExchangeTaxCollectorEquipmentStartedEvent(_message.Message):
    __slots__ = ("tax_collector_information",)
    TAX_COLLECTOR_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    tax_collector_information: _common_pb2.TaxCollectorInformation
    def __init__(self, tax_collector_information: _Optional[_Union[_common_pb2.TaxCollectorInformation, _Mapping]] = ...) -> None: ...

class ExchangeNpcTradeStartedEvent(_message.Message):
    __slots__ = ("npc_id",)
    NPC_ID_FIELD_NUMBER: _ClassVar[int]
    npc_id: int
    def __init__(self, npc_id: _Optional[int] = ...) -> None: ...

class ExchangeRunesTradeStartedEvent(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ExchangeRecycleTradeStartedEvent(_message.Message):
    __slots__ = ("percent_to_prism", "percent_to_player", "adjacent_subareas_possessed", "adjacent_subareas_not_possessed")
    PERCENT_TO_PRISM_FIELD_NUMBER: _ClassVar[int]
    PERCENT_TO_PLAYER_FIELD_NUMBER: _ClassVar[int]
    ADJACENT_SUBAREAS_POSSESSED_FIELD_NUMBER: _ClassVar[int]
    ADJACENT_SUBAREAS_NOT_POSSESSED_FIELD_NUMBER: _ClassVar[int]
    percent_to_prism: int
    percent_to_player: int
    adjacent_subareas_possessed: _containers.RepeatedScalarFieldContainer[int]
    adjacent_subareas_not_possessed: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, percent_to_prism: _Optional[int] = ..., percent_to_player: _Optional[int] = ..., adjacent_subareas_possessed: _Optional[_Iterable[int]] = ..., adjacent_subareas_not_possessed: _Optional[_Iterable[int]] = ...) -> None: ...

class ExchangeNpcShopStartedEvent(_message.Message):
    __slots__ = ("npc_seller_id", "token_id", "objects")
    NPC_SELLER_ID_FIELD_NUMBER: _ClassVar[int]
    TOKEN_ID_FIELD_NUMBER: _ClassVar[int]
    OBJECTS_FIELD_NUMBER: _ClassVar[int]
    npc_seller_id: int
    token_id: int
    objects: _containers.RepeatedCompositeFieldContainer[_common_pb2.ItemMinimalInformation]
    def __init__(self, npc_seller_id: _Optional[int] = ..., token_id: _Optional[int] = ..., objects: _Optional[_Iterable[_Union[_common_pb2.ItemMinimalInformation, _Mapping]]] = ...) -> None: ...

class ExchangeMultiCraftOkEvent(_message.Message):
    __slots__ = ("initiator_id", "other_id", "role")
    INITIATOR_ID_FIELD_NUMBER: _ClassVar[int]
    OTHER_ID_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    initiator_id: int
    other_id: int
    role: _common_pb2.ExchangeType
    def __init__(self, initiator_id: _Optional[int] = ..., other_id: _Optional[int] = ..., role: _Optional[_Union[_common_pb2.ExchangeType, str]] = ...) -> None: ...

class ExchangeCraftResultEvent(_message.Message):
    __slots__ = ("result", "object_gid", "object")
    class CraftResult(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        IMPOSSIBLE: _ClassVar[ExchangeCraftResultEvent.CraftResult]
        FAILED: _ClassVar[ExchangeCraftResultEvent.CraftResult]
        SUCCESS: _ClassVar[ExchangeCraftResultEvent.CraftResult]
        NEUTRAL: _ClassVar[ExchangeCraftResultEvent.CraftResult]
        FORBIDDEN: _ClassVar[ExchangeCraftResultEvent.CraftResult]
    IMPOSSIBLE: ExchangeCraftResultEvent.CraftResult
    FAILED: ExchangeCraftResultEvent.CraftResult
    SUCCESS: ExchangeCraftResultEvent.CraftResult
    NEUTRAL: ExchangeCraftResultEvent.CraftResult
    FORBIDDEN: ExchangeCraftResultEvent.CraftResult
    class ExchangeCraftResultWithObjectDescription(_message.Message):
        __slots__ = ("object", "magic_pool_status", "fm_power")
        class MagicPoolStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            NO_CHANGE: _ClassVar[ExchangeCraftResultEvent.ExchangeCraftResultWithObjectDescription.MagicPoolStatus]
            INCREASE: _ClassVar[ExchangeCraftResultEvent.ExchangeCraftResultWithObjectDescription.MagicPoolStatus]
            LOSS: _ClassVar[ExchangeCraftResultEvent.ExchangeCraftResultWithObjectDescription.MagicPoolStatus]
        NO_CHANGE: ExchangeCraftResultEvent.ExchangeCraftResultWithObjectDescription.MagicPoolStatus
        INCREASE: ExchangeCraftResultEvent.ExchangeCraftResultWithObjectDescription.MagicPoolStatus
        LOSS: ExchangeCraftResultEvent.ExchangeCraftResultWithObjectDescription.MagicPoolStatus
        OBJECT_FIELD_NUMBER: _ClassVar[int]
        MAGIC_POOL_STATUS_FIELD_NUMBER: _ClassVar[int]
        FM_POWER_FIELD_NUMBER: _ClassVar[int]
        object: _common_pb2.ObjectItem
        magic_pool_status: ExchangeCraftResultEvent.ExchangeCraftResultWithObjectDescription.MagicPoolStatus
        fm_power: float
        def __init__(self, object: _Optional[_Union[_common_pb2.ObjectItem, _Mapping]] = ..., magic_pool_status: _Optional[_Union[ExchangeCraftResultEvent.ExchangeCraftResultWithObjectDescription.MagicPoolStatus, str]] = ..., fm_power: _Optional[float] = ...) -> None: ...
    RESULT_FIELD_NUMBER: _ClassVar[int]
    OBJECT_GID_FIELD_NUMBER: _ClassVar[int]
    OBJECT_FIELD_NUMBER: _ClassVar[int]
    result: ExchangeCraftResultEvent.CraftResult
    object_gid: int
    object: ExchangeCraftResultEvent.ExchangeCraftResultWithObjectDescription
    def __init__(self, result: _Optional[_Union[ExchangeCraftResultEvent.CraftResult, str]] = ..., object_gid: _Optional[int] = ..., object: _Optional[_Union[ExchangeCraftResultEvent.ExchangeCraftResultWithObjectDescription, _Mapping]] = ...) -> None: ...

class ExchangeMountStockStartedEvent(_message.Message):
    __slots__ = ("objects",)
    OBJECTS_FIELD_NUMBER: _ClassVar[int]
    objects: _containers.RepeatedCompositeFieldContainer[_common_pb2.ObjectItemInventory]
    def __init__(self, objects: _Optional[_Iterable[_Union[_common_pb2.ObjectItemInventory, _Mapping]]] = ...) -> None: ...

class ExchangeTaxCollectorShopStartedEvent(_message.Message):
    __slots__ = ("objects", "kamas")
    OBJECTS_FIELD_NUMBER: _ClassVar[int]
    KAMAS_FIELD_NUMBER: _ClassVar[int]
    objects: _containers.RepeatedCompositeFieldContainer[_common_pb2.ObjectItemInventory]
    kamas: int
    def __init__(self, objects: _Optional[_Iterable[_Union[_common_pb2.ObjectItemInventory, _Mapping]]] = ..., kamas: _Optional[int] = ...) -> None: ...

class ExchangeBidSellerStartedEvent(_message.Message):
    __slots__ = ("selling_conditions", "items")
    class ItemToSellInBid(_message.Message):
        __slots__ = ("item", "price", "unsold_delay")
        ITEM_FIELD_NUMBER: _ClassVar[int]
        PRICE_FIELD_NUMBER: _ClassVar[int]
        UNSOLD_DELAY_FIELD_NUMBER: _ClassVar[int]
        item: BidItem
        price: int
        unsold_delay: int
        def __init__(self, item: _Optional[_Union[BidItem, _Mapping]] = ..., price: _Optional[int] = ..., unsold_delay: _Optional[int] = ...) -> None: ...
    SELLING_CONDITIONS_FIELD_NUMBER: _ClassVar[int]
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    selling_conditions: SellingConditions
    items: _containers.RepeatedCompositeFieldContainer[ExchangeBidSellerStartedEvent.ItemToSellInBid]
    def __init__(self, selling_conditions: _Optional[_Union[SellingConditions, _Mapping]] = ..., items: _Optional[_Iterable[_Union[ExchangeBidSellerStartedEvent.ItemToSellInBid, _Mapping]]] = ...) -> None: ...

class BidItem(_message.Message):
    __slots__ = ("uid", "quantity", "gid", "effects")
    UID_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    GID_FIELD_NUMBER: _ClassVar[int]
    EFFECTS_FIELD_NUMBER: _ClassVar[int]
    uid: int
    quantity: int
    gid: int
    effects: _containers.RepeatedCompositeFieldContainer[_common_pb2.ObjectEffect]
    def __init__(self, uid: _Optional[int] = ..., quantity: _Optional[int] = ..., gid: _Optional[int] = ..., effects: _Optional[_Iterable[_Union[_common_pb2.ObjectEffect, _Mapping]]] = ...) -> None: ...

class ExchangeBidBuyerStartedEvent(_message.Message):
    __slots__ = ("selling_conditions",)
    SELLING_CONDITIONS_FIELD_NUMBER: _ClassVar[int]
    selling_conditions: SellingConditions
    def __init__(self, selling_conditions: _Optional[_Union[SellingConditions, _Mapping]] = ...) -> None: ...

class ExchangeBidPriceEvent(_message.Message):
    __slots__ = ("object_gid", "average_price", "bid_price_for_seller")
    class BidPriceForSeller(_message.Message):
        __slots__ = ("all_identical", "minimal_prices")
        ALL_IDENTICAL_FIELD_NUMBER: _ClassVar[int]
        MINIMAL_PRICES_FIELD_NUMBER: _ClassVar[int]
        all_identical: bool
        minimal_prices: _containers.RepeatedScalarFieldContainer[int]
        def __init__(self, all_identical: bool = ..., minimal_prices: _Optional[_Iterable[int]] = ...) -> None: ...
    OBJECT_GID_FIELD_NUMBER: _ClassVar[int]
    AVERAGE_PRICE_FIELD_NUMBER: _ClassVar[int]
    BID_PRICE_FOR_SELLER_FIELD_NUMBER: _ClassVar[int]
    object_gid: int
    average_price: int
    bid_price_for_seller: ExchangeBidPriceEvent.BidPriceForSeller
    def __init__(self, object_gid: _Optional[int] = ..., average_price: _Optional[int] = ..., bid_price_for_seller: _Optional[_Union[ExchangeBidPriceEvent.BidPriceForSeller, _Mapping]] = ...) -> None: ...

class ExchangeTypesExchangerDescriptionForUserEvent(_message.Message):
    __slots__ = ("object_type", "type_description")
    OBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    TYPE_DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    object_type: int
    type_description: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, object_type: _Optional[int] = ..., type_description: _Optional[_Iterable[int]] = ...) -> None: ...

class ExchangeTypesItemsExchangerDescriptionForUserEvent(_message.Message):
    __slots__ = ("object_gid", "object_type", "item_descriptions")
    class BidExchangerObject(_message.Message):
        __slots__ = ("uid", "gid", "type", "effects", "prices")
        UID_FIELD_NUMBER: _ClassVar[int]
        GID_FIELD_NUMBER: _ClassVar[int]
        TYPE_FIELD_NUMBER: _ClassVar[int]
        EFFECTS_FIELD_NUMBER: _ClassVar[int]
        PRICES_FIELD_NUMBER: _ClassVar[int]
        uid: int
        gid: int
        type: int
        effects: _containers.RepeatedCompositeFieldContainer[_common_pb2.ObjectEffect]
        prices: _containers.RepeatedScalarFieldContainer[int]
        def __init__(self, uid: _Optional[int] = ..., gid: _Optional[int] = ..., type: _Optional[int] = ..., effects: _Optional[_Iterable[_Union[_common_pb2.ObjectEffect, _Mapping]]] = ..., prices: _Optional[_Iterable[int]] = ...) -> None: ...
    OBJECT_GID_FIELD_NUMBER: _ClassVar[int]
    OBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    ITEM_DESCRIPTIONS_FIELD_NUMBER: _ClassVar[int]
    object_gid: int
    object_type: int
    item_descriptions: _containers.RepeatedCompositeFieldContainer[ExchangeTypesItemsExchangerDescriptionForUserEvent.BidExchangerObject]
    def __init__(self, object_gid: _Optional[int] = ..., object_type: _Optional[int] = ..., item_descriptions: _Optional[_Iterable[_Union[ExchangeTypesItemsExchangerDescriptionForUserEvent.BidExchangerObject, _Mapping]]] = ...) -> None: ...

class ExchangeWeightEvent(_message.Message):
    __slots__ = ("current_weight", "max_weight")
    CURRENT_WEIGHT_FIELD_NUMBER: _ClassVar[int]
    MAX_WEIGHT_FIELD_NUMBER: _ClassVar[int]
    current_weight: int
    max_weight: int
    def __init__(self, current_weight: _Optional[int] = ..., max_weight: _Optional[int] = ...) -> None: ...

class ExchangeTaxCollectorGetEvent(_message.Message):
    __slots__ = ("collector_name", "coordinates", "user_name", "caller_id", "caller_name", "pods", "objects", "look")
    COLLECTOR_NAME_FIELD_NUMBER: _ClassVar[int]
    COORDINATES_FIELD_NUMBER: _ClassVar[int]
    USER_NAME_FIELD_NUMBER: _ClassVar[int]
    CALLER_ID_FIELD_NUMBER: _ClassVar[int]
    CALLER_NAME_FIELD_NUMBER: _ClassVar[int]
    PODS_FIELD_NUMBER: _ClassVar[int]
    OBJECTS_FIELD_NUMBER: _ClassVar[int]
    LOOK_FIELD_NUMBER: _ClassVar[int]
    collector_name: str
    coordinates: _common_pb2.MapExtendedCoordinates
    user_name: str
    caller_id: int
    caller_name: str
    pods: int
    objects: _containers.RepeatedCompositeFieldContainer[_common_pb2.ObjectGidWithQuantity]
    look: _common_pb2.EntityLook
    def __init__(self, collector_name: _Optional[str] = ..., coordinates: _Optional[_Union[_common_pb2.MapExtendedCoordinates, _Mapping]] = ..., user_name: _Optional[str] = ..., caller_id: _Optional[int] = ..., caller_name: _Optional[str] = ..., pods: _Optional[int] = ..., objects: _Optional[_Iterable[_Union[_common_pb2.ObjectGidWithQuantity, _Mapping]]] = ..., look: _Optional[_Union[_common_pb2.EntityLook, _Mapping]] = ...) -> None: ...

class ExchangeBoughtEvent(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ExchangeSoldEvent(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ExchangeMountWithoutPaddockStartedEvent(_message.Message):
    __slots__ = ("stabled_mounts", "paddocked_mounts")
    STABLED_MOUNTS_FIELD_NUMBER: _ClassVar[int]
    PADDOCKED_MOUNTS_FIELD_NUMBER: _ClassVar[int]
    stabled_mounts: _containers.RepeatedCompositeFieldContainer[_common_pb2.MountData]
    paddocked_mounts: _containers.RepeatedCompositeFieldContainer[_common_pb2.MountData]
    def __init__(self, stabled_mounts: _Optional[_Iterable[_Union[_common_pb2.MountData, _Mapping]]] = ..., paddocked_mounts: _Optional[_Iterable[_Union[_common_pb2.MountData, _Mapping]]] = ...) -> None: ...

class ExchangeMountsStableAddedEvent(_message.Message):
    __slots__ = ("mounts", "new_born")
    MOUNTS_FIELD_NUMBER: _ClassVar[int]
    NEW_BORN_FIELD_NUMBER: _ClassVar[int]
    mounts: _containers.RepeatedCompositeFieldContainer[_common_pb2.MountData]
    new_born: bool
    def __init__(self, mounts: _Optional[_Iterable[_Union[_common_pb2.MountData, _Mapping]]] = ..., new_born: bool = ...) -> None: ...

class ExchangeMountsPaddockAddedEvent(_message.Message):
    __slots__ = ("mounts",)
    MOUNTS_FIELD_NUMBER: _ClassVar[int]
    mounts: _containers.RepeatedCompositeFieldContainer[_common_pb2.MountData]
    def __init__(self, mounts: _Optional[_Iterable[_Union[_common_pb2.MountData, _Mapping]]] = ...) -> None: ...

class ExchangeMountsStableRemoveEvent(_message.Message):
    __slots__ = ("mounts_id",)
    MOUNTS_ID_FIELD_NUMBER: _ClassVar[int]
    mounts_id: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, mounts_id: _Optional[_Iterable[int]] = ...) -> None: ...

class ExchangeMountsPaddockRemoveEvent(_message.Message):
    __slots__ = ("mounts_id",)
    MOUNTS_ID_FIELD_NUMBER: _ClassVar[int]
    mounts_id: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, mounts_id: _Optional[_Iterable[int]] = ...) -> None: ...

class ExchangeMountFreeFromPaddockEvent(_message.Message):
    __slots__ = ("name", "coordinates", "liberator")
    NAME_FIELD_NUMBER: _ClassVar[int]
    COORDINATES_FIELD_NUMBER: _ClassVar[int]
    LIBERATOR_FIELD_NUMBER: _ClassVar[int]
    name: str
    coordinates: _common_pb2.MapCoordinates
    liberator: str
    def __init__(self, name: _Optional[str] = ..., coordinates: _Optional[_Union[_common_pb2.MapCoordinates, _Mapping]] = ..., liberator: _Optional[str] = ...) -> None: ...

class ExchangeItemAutoCraftStoppedEvent(_message.Message):
    __slots__ = ("reason",)
    class ExchangeReplayStopReason(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        OK: _ClassVar[ExchangeItemAutoCraftStoppedEvent.ExchangeReplayStopReason]
        USER: _ClassVar[ExchangeItemAutoCraftStoppedEvent.ExchangeReplayStopReason]
        MISSING_RESSOURCE: _ClassVar[ExchangeItemAutoCraftStoppedEvent.ExchangeReplayStopReason]
        IMPOSSIBLE_MODIFICATION: _ClassVar[ExchangeItemAutoCraftStoppedEvent.ExchangeReplayStopReason]
    OK: ExchangeItemAutoCraftStoppedEvent.ExchangeReplayStopReason
    USER: ExchangeItemAutoCraftStoppedEvent.ExchangeReplayStopReason
    MISSING_RESSOURCE: ExchangeItemAutoCraftStoppedEvent.ExchangeReplayStopReason
    IMPOSSIBLE_MODIFICATION: ExchangeItemAutoCraftStoppedEvent.ExchangeReplayStopReason
    REASON_FIELD_NUMBER: _ClassVar[int]
    reason: ExchangeItemAutoCraftStoppedEvent.ExchangeReplayStopReason
    def __init__(self, reason: _Optional[_Union[ExchangeItemAutoCraftStoppedEvent.ExchangeReplayStopReason, str]] = ...) -> None: ...

class ExchangeCraftStartedEvent(_message.Message):
    __slots__ = ("skill_id",)
    SKILL_ID_FIELD_NUMBER: _ClassVar[int]
    skill_id: int
    def __init__(self, skill_id: _Optional[int] = ...) -> None: ...

class ExchangeMultiCraftCrafterStartedEvent(_message.Message):
    __slots__ = ("skill_id",)
    SKILL_ID_FIELD_NUMBER: _ClassVar[int]
    skill_id: int
    def __init__(self, skill_id: _Optional[int] = ...) -> None: ...

class ExchangeMultiCraftCustomerStartedEvent(_message.Message):
    __slots__ = ("skill_id", "crafter_job_level")
    SKILL_ID_FIELD_NUMBER: _ClassVar[int]
    CRAFTER_JOB_LEVEL_FIELD_NUMBER: _ClassVar[int]
    skill_id: int
    crafter_job_level: int
    def __init__(self, skill_id: _Optional[int] = ..., crafter_job_level: _Optional[int] = ...) -> None: ...

class ExchangeCrafterJobLevelUpEvent(_message.Message):
    __slots__ = ("crafter_job_level",)
    CRAFTER_JOB_LEVEL_FIELD_NUMBER: _ClassVar[int]
    crafter_job_level: int
    def __init__(self, crafter_job_level: _Optional[int] = ...) -> None: ...

class ExchangeJobIndexStartedEvent(_message.Message):
    __slots__ = ("jobs",)
    JOBS_FIELD_NUMBER: _ClassVar[int]
    jobs: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, jobs: _Optional[_Iterable[int]] = ...) -> None: ...

class ExchangeCraftPaymentModifiedEvent(_message.Message):
    __slots__ = ("kamas",)
    KAMAS_FIELD_NUMBER: _ClassVar[int]
    kamas: int
    def __init__(self, kamas: _Optional[int] = ...) -> None: ...

class SellingConditions(_message.Message):
    __slots__ = ("quantities", "types", "tax_percentage", "tax_modification_percentage", "max_item_level", "max_item_per_account", "npc_contextual_id", "unsold_delay")
    QUANTITIES_FIELD_NUMBER: _ClassVar[int]
    TYPES_FIELD_NUMBER: _ClassVar[int]
    TAX_PERCENTAGE_FIELD_NUMBER: _ClassVar[int]
    TAX_MODIFICATION_PERCENTAGE_FIELD_NUMBER: _ClassVar[int]
    MAX_ITEM_LEVEL_FIELD_NUMBER: _ClassVar[int]
    MAX_ITEM_PER_ACCOUNT_FIELD_NUMBER: _ClassVar[int]
    NPC_CONTEXTUAL_ID_FIELD_NUMBER: _ClassVar[int]
    UNSOLD_DELAY_FIELD_NUMBER: _ClassVar[int]
    quantities: _containers.RepeatedScalarFieldContainer[int]
    types: _containers.RepeatedScalarFieldContainer[int]
    tax_percentage: float
    tax_modification_percentage: float
    max_item_level: int
    max_item_per_account: int
    npc_contextual_id: int
    unsold_delay: int
    def __init__(self, quantities: _Optional[_Iterable[int]] = ..., types: _Optional[_Iterable[int]] = ..., tax_percentage: _Optional[float] = ..., tax_modification_percentage: _Optional[float] = ..., max_item_level: _Optional[int] = ..., max_item_per_account: _Optional[int] = ..., npc_contextual_id: _Optional[int] = ..., unsold_delay: _Optional[int] = ...) -> None: ...

class ObjectAveragePricesErrorEvent(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ObjectAveragePricesEvent(_message.Message):
    __slots__ = ("objects_average_prices",)
    class ObjectAveragePrice(_message.Message):
        __slots__ = ("object_gid", "average_price")
        OBJECT_GID_FIELD_NUMBER: _ClassVar[int]
        AVERAGE_PRICE_FIELD_NUMBER: _ClassVar[int]
        object_gid: int
        average_price: int
        def __init__(self, object_gid: _Optional[int] = ..., average_price: _Optional[int] = ...) -> None: ...
    OBJECTS_AVERAGE_PRICES_FIELD_NUMBER: _ClassVar[int]
    objects_average_prices: _containers.RepeatedCompositeFieldContainer[ObjectAveragePricesEvent.ObjectAveragePrice]
    def __init__(self, objects_average_prices: _Optional[_Iterable[_Union[ObjectAveragePricesEvent.ObjectAveragePrice, _Mapping]]] = ...) -> None: ...

class RecycleResultEvent(_message.Message):
    __slots__ = ("prism_nuggets", "player_nuggets")
    PRISM_NUGGETS_FIELD_NUMBER: _ClassVar[int]
    PLAYER_NUGGETS_FIELD_NUMBER: _ClassVar[int]
    prism_nuggets: int
    player_nuggets: int
    def __init__(self, prism_nuggets: _Optional[int] = ..., player_nuggets: _Optional[int] = ...) -> None: ...

class DecraftResultEvent(_message.Message):
    __slots__ = ("results",)
    class DecraftedItem(_message.Message):
        __slots__ = ("object_uid", "bonus_min", "bonus_max", "runes")
        class Rune(_message.Message):
            __slots__ = ("rune_id", "quantity")
            RUNE_ID_FIELD_NUMBER: _ClassVar[int]
            QUANTITY_FIELD_NUMBER: _ClassVar[int]
            rune_id: int
            quantity: int
            def __init__(self, rune_id: _Optional[int] = ..., quantity: _Optional[int] = ...) -> None: ...
        OBJECT_UID_FIELD_NUMBER: _ClassVar[int]
        BONUS_MIN_FIELD_NUMBER: _ClassVar[int]
        BONUS_MAX_FIELD_NUMBER: _ClassVar[int]
        RUNES_FIELD_NUMBER: _ClassVar[int]
        object_uid: int
        bonus_min: float
        bonus_max: float
        runes: _containers.RepeatedCompositeFieldContainer[DecraftResultEvent.DecraftedItem.Rune]
        def __init__(self, object_uid: _Optional[int] = ..., bonus_min: _Optional[float] = ..., bonus_max: _Optional[float] = ..., runes: _Optional[_Iterable[_Union[DecraftResultEvent.DecraftedItem.Rune, _Mapping]]] = ...) -> None: ...
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    results: _containers.RepeatedCompositeFieldContainer[DecraftResultEvent.DecraftedItem]
    def __init__(self, results: _Optional[_Iterable[_Union[DecraftResultEvent.DecraftedItem, _Mapping]]] = ...) -> None: ...
