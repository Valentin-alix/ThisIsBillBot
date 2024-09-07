from com.ankama.dofus.server.game.protocol import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ShortcutBarAddRequest(_message.Message):
    __slots__ = ("bar_type", "shortcut")
    BAR_TYPE_FIELD_NUMBER: _ClassVar[int]
    SHORTCUT_FIELD_NUMBER: _ClassVar[int]
    bar_type: _common_pb2.ShortcutBar
    shortcut: _common_pb2.Shortcut
    def __init__(self, bar_type: _Optional[_Union[_common_pb2.ShortcutBar, str]] = ..., shortcut: _Optional[_Union[_common_pb2.Shortcut, _Mapping]] = ...) -> None: ...

class ShortcutBarRemoveRequest(_message.Message):
    __slots__ = ("bar_type", "slot_id")
    BAR_TYPE_FIELD_NUMBER: _ClassVar[int]
    SLOT_ID_FIELD_NUMBER: _ClassVar[int]
    bar_type: _common_pb2.ShortcutBar
    slot_id: int
    def __init__(self, bar_type: _Optional[_Union[_common_pb2.ShortcutBar, str]] = ..., slot_id: _Optional[int] = ...) -> None: ...

class ShortcutBarSwapRequest(_message.Message):
    __slots__ = ("bar_type", "first_slot_id", "second_slot_id")
    BAR_TYPE_FIELD_NUMBER: _ClassVar[int]
    FIRST_SLOT_ID_FIELD_NUMBER: _ClassVar[int]
    SECOND_SLOT_ID_FIELD_NUMBER: _ClassVar[int]
    bar_type: _common_pb2.ShortcutBar
    first_slot_id: int
    second_slot_id: int
    def __init__(self, bar_type: _Optional[_Union[_common_pb2.ShortcutBar, str]] = ..., first_slot_id: _Optional[int] = ..., second_slot_id: _Optional[int] = ...) -> None: ...

class ObjectSetPositionRequest(_message.Message):
    __slots__ = ("object_uid", "position", "quantity")
    OBJECT_UID_FIELD_NUMBER: _ClassVar[int]
    POSITION_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    object_uid: int
    position: int
    quantity: int
    def __init__(self, object_uid: _Optional[int] = ..., position: _Optional[int] = ..., quantity: _Optional[int] = ...) -> None: ...

class ObjectDropRequest(_message.Message):
    __slots__ = ("object",)
    OBJECT_FIELD_NUMBER: _ClassVar[int]
    object: _common_pb2.ObjectUidWithQuantity
    def __init__(self, object: _Optional[_Union[_common_pb2.ObjectUidWithQuantity, _Mapping]] = ...) -> None: ...

class ObjectDeleteRequest(_message.Message):
    __slots__ = ("object",)
    OBJECT_FIELD_NUMBER: _ClassVar[int]
    object: _common_pb2.ObjectUidWithQuantity
    def __init__(self, object: _Optional[_Union[_common_pb2.ObjectUidWithQuantity, _Mapping]] = ...) -> None: ...

class ObjectUseRequest(_message.Message):
    __slots__ = ("object_uid",)
    OBJECT_UID_FIELD_NUMBER: _ClassVar[int]
    object_uid: int
    def __init__(self, object_uid: _Optional[int] = ...) -> None: ...

class ObjectUseMultipleRequest(_message.Message):
    __slots__ = ("object_uid", "quantity")
    OBJECT_UID_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    object_uid: int
    quantity: int
    def __init__(self, object_uid: _Optional[int] = ..., quantity: _Optional[int] = ...) -> None: ...

class ObjectUseOnCharacterRequest(_message.Message):
    __slots__ = ("object_uid", "player_id")
    OBJECT_UID_FIELD_NUMBER: _ClassVar[int]
    PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
    object_uid: int
    player_id: int
    def __init__(self, object_uid: _Optional[int] = ..., player_id: _Optional[int] = ...) -> None: ...

class ObjectUseOnCellRequest(_message.Message):
    __slots__ = ("object_uid", "cell_id")
    OBJECT_UID_FIELD_NUMBER: _ClassVar[int]
    CELL_ID_FIELD_NUMBER: _ClassVar[int]
    object_uid: int
    cell_id: int
    def __init__(self, object_uid: _Optional[int] = ..., cell_id: _Optional[int] = ...) -> None: ...

class ObjectFeedRequest(_message.Message):
    __slots__ = ("object_uid", "meal")
    OBJECT_UID_FIELD_NUMBER: _ClassVar[int]
    MEAL_FIELD_NUMBER: _ClassVar[int]
    object_uid: int
    meal: _containers.RepeatedCompositeFieldContainer[_common_pb2.ObjectUidWithQuantity]
    def __init__(self, object_uid: _Optional[int] = ..., meal: _Optional[_Iterable[_Union[_common_pb2.ObjectUidWithQuantity, _Mapping]]] = ...) -> None: ...

class ObjectFavoriteRequest(_message.Message):
    __slots__ = ("objects", "favorite")
    class ObjectFavorite(_message.Message):
        __slots__ = ("object_uid", "position")
        OBJECT_UID_FIELD_NUMBER: _ClassVar[int]
        POSITION_FIELD_NUMBER: _ClassVar[int]
        object_uid: int
        position: int
        def __init__(self, object_uid: _Optional[int] = ..., position: _Optional[int] = ...) -> None: ...
    OBJECTS_FIELD_NUMBER: _ClassVar[int]
    FAVORITE_FIELD_NUMBER: _ClassVar[int]
    objects: _containers.RepeatedCompositeFieldContainer[ObjectFavoriteRequest.ObjectFavorite]
    favorite: bool
    def __init__(self, objects: _Optional[_Iterable[_Union[ObjectFavoriteRequest.ObjectFavorite, _Mapping]]] = ..., favorite: bool = ...) -> None: ...

class KamasUpdateEvent(_message.Message):
    __slots__ = ("quantity",)
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    quantity: int
    def __init__(self, quantity: _Optional[int] = ...) -> None: ...

class ObjectDroppedEvent(_message.Message):
    __slots__ = ("object",)
    OBJECT_FIELD_NUMBER: _ClassVar[int]
    object: _common_pb2.ObjectInRolePlay
    def __init__(self, object: _Optional[_Union[_common_pb2.ObjectInRolePlay, _Mapping]] = ...) -> None: ...

class ObjectsDroppedEvent(_message.Message):
    __slots__ = ("object",)
    OBJECT_FIELD_NUMBER: _ClassVar[int]
    object: _containers.RepeatedCompositeFieldContainer[_common_pb2.ObjectInRolePlay]
    def __init__(self, object: _Optional[_Iterable[_Union[_common_pb2.ObjectInRolePlay, _Mapping]]] = ...) -> None: ...

class ObjectCellDeleteEvent(_message.Message):
    __slots__ = ("cell_id",)
    CELL_ID_FIELD_NUMBER: _ClassVar[int]
    cell_id: int
    def __init__(self, cell_id: _Optional[int] = ...) -> None: ...

class ObjectCellsDeleteEvent(_message.Message):
    __slots__ = ("cells_id",)
    CELLS_ID_FIELD_NUMBER: _ClassVar[int]
    cells_id: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, cells_id: _Optional[_Iterable[int]] = ...) -> None: ...

class ObjectMovementEvent(_message.Message):
    __slots__ = ("object_uid", "position")
    OBJECT_UID_FIELD_NUMBER: _ClassVar[int]
    POSITION_FIELD_NUMBER: _ClassVar[int]
    object_uid: int
    position: int
    def __init__(self, object_uid: _Optional[int] = ..., position: _Optional[int] = ...) -> None: ...

class ObjectAddedEvent(_message.Message):
    __slots__ = ("object", "origin")
    OBJECT_FIELD_NUMBER: _ClassVar[int]
    ORIGIN_FIELD_NUMBER: _ClassVar[int]
    object: _common_pb2.ObjectItemInventory
    origin: _common_pb2.ObjectOrigin
    def __init__(self, object: _Optional[_Union[_common_pb2.ObjectItemInventory, _Mapping]] = ..., origin: _Optional[_Union[_common_pb2.ObjectOrigin, str]] = ...) -> None: ...

class ObjectsAddedEvent(_message.Message):
    __slots__ = ("objects",)
    OBJECTS_FIELD_NUMBER: _ClassVar[int]
    objects: _containers.RepeatedCompositeFieldContainer[_common_pb2.ObjectItemInventory]
    def __init__(self, objects: _Optional[_Iterable[_Union[_common_pb2.ObjectItemInventory, _Mapping]]] = ...) -> None: ...

class GoldAddedEvent(_message.Message):
    __slots__ = ("sum",)
    SUM_FIELD_NUMBER: _ClassVar[int]
    sum: int
    def __init__(self, sum: _Optional[int] = ...) -> None: ...

class ObjectErrorEvent(_message.Message):
    __slots__ = ("reason",)
    REASON_FIELD_NUMBER: _ClassVar[int]
    reason: _common_pb2.ObjectError
    def __init__(self, reason: _Optional[_Union[_common_pb2.ObjectError, str]] = ...) -> None: ...

class ObjectDeletedEvent(_message.Message):
    __slots__ = ("object_uid",)
    OBJECT_UID_FIELD_NUMBER: _ClassVar[int]
    object_uid: int
    def __init__(self, object_uid: _Optional[int] = ...) -> None: ...

class ObjectsDeletedEvent(_message.Message):
    __slots__ = ("objects_uid",)
    OBJECTS_UID_FIELD_NUMBER: _ClassVar[int]
    objects_uid: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, objects_uid: _Optional[_Iterable[int]] = ...) -> None: ...

class ObjectQuantityEvent(_message.Message):
    __slots__ = ("object", "origin")
    OBJECT_FIELD_NUMBER: _ClassVar[int]
    ORIGIN_FIELD_NUMBER: _ClassVar[int]
    object: _common_pb2.ObjectUidWithQuantity
    origin: _common_pb2.ObjectOrigin
    def __init__(self, object: _Optional[_Union[_common_pb2.ObjectUidWithQuantity, _Mapping]] = ..., origin: _Optional[_Union[_common_pb2.ObjectOrigin, str]] = ...) -> None: ...

class ObjectsQuantityEvent(_message.Message):
    __slots__ = ("object",)
    OBJECT_FIELD_NUMBER: _ClassVar[int]
    object: _containers.RepeatedCompositeFieldContainer[_common_pb2.ObjectUidWithQuantity]
    def __init__(self, object: _Optional[_Iterable[_Union[_common_pb2.ObjectUidWithQuantity, _Mapping]]] = ...) -> None: ...

class ObjectModifiedEvent(_message.Message):
    __slots__ = ("object",)
    OBJECT_FIELD_NUMBER: _ClassVar[int]
    object: _common_pb2.ObjectItemInventory
    def __init__(self, object: _Optional[_Union[_common_pb2.ObjectItemInventory, _Mapping]] = ...) -> None: ...

class ObjectFavoriteResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: bool
    def __init__(self, result: bool = ...) -> None: ...

class ObjectHarvestedEvent(_message.Message):
    __slots__ = ("object_gid", "quantity")
    OBJECT_GID_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    object_gid: int
    quantity: int
    def __init__(self, object_gid: _Optional[int] = ..., quantity: _Optional[int] = ...) -> None: ...

class ObjectHarvestedWithBonusEvent(_message.Message):
    __slots__ = ("object_gid", "quantity", "bonus_quantity")
    OBJECT_GID_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    BONUS_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    object_gid: int
    quantity: int
    bonus_quantity: int
    def __init__(self, object_gid: _Optional[int] = ..., quantity: _Optional[int] = ..., bonus_quantity: _Optional[int] = ...) -> None: ...

class InventoryContentEvent(_message.Message):
    __slots__ = ("objects", "kamas")
    OBJECTS_FIELD_NUMBER: _ClassVar[int]
    KAMAS_FIELD_NUMBER: _ClassVar[int]
    objects: _containers.RepeatedCompositeFieldContainer[_common_pb2.ObjectItemInventory]
    kamas: int
    def __init__(self, objects: _Optional[_Iterable[_Union[_common_pb2.ObjectItemInventory, _Mapping]]] = ..., kamas: _Optional[int] = ...) -> None: ...

class InventoryContentWatchEvent(_message.Message):
    __slots__ = ("objects", "kamas")
    OBJECTS_FIELD_NUMBER: _ClassVar[int]
    KAMAS_FIELD_NUMBER: _ClassVar[int]
    objects: _containers.RepeatedCompositeFieldContainer[_common_pb2.ObjectItemInventory]
    kamas: int
    def __init__(self, objects: _Optional[_Iterable[_Union[_common_pb2.ObjectItemInventory, _Mapping]]] = ..., kamas: _Optional[int] = ...) -> None: ...

class InventoryWeightEvent(_message.Message):
    __slots__ = ("inventory_weight", "weight_max")
    INVENTORY_WEIGHT_FIELD_NUMBER: _ClassVar[int]
    WEIGHT_MAX_FIELD_NUMBER: _ClassVar[int]
    inventory_weight: int
    weight_max: int
    def __init__(self, inventory_weight: _Optional[int] = ..., weight_max: _Optional[int] = ...) -> None: ...

class ShortcutBarContentEvent(_message.Message):
    __slots__ = ("bar_type", "shortcuts")
    BAR_TYPE_FIELD_NUMBER: _ClassVar[int]
    SHORTCUTS_FIELD_NUMBER: _ClassVar[int]
    bar_type: _common_pb2.ShortcutBar
    shortcuts: _containers.RepeatedCompositeFieldContainer[_common_pb2.Shortcut]
    def __init__(self, bar_type: _Optional[_Union[_common_pb2.ShortcutBar, str]] = ..., shortcuts: _Optional[_Iterable[_Union[_common_pb2.Shortcut, _Mapping]]] = ...) -> None: ...

class ShortcutBarRefreshEvent(_message.Message):
    __slots__ = ("bar_type", "shortcut")
    BAR_TYPE_FIELD_NUMBER: _ClassVar[int]
    SHORTCUT_FIELD_NUMBER: _ClassVar[int]
    bar_type: _common_pb2.ShortcutBar
    shortcut: _common_pb2.Shortcut
    def __init__(self, bar_type: _Optional[_Union[_common_pb2.ShortcutBar, str]] = ..., shortcut: _Optional[_Union[_common_pb2.Shortcut, _Mapping]] = ...) -> None: ...

class ShortcutBarRemovedEvent(_message.Message):
    __slots__ = ("bar_type", "slot_id")
    BAR_TYPE_FIELD_NUMBER: _ClassVar[int]
    SLOT_ID_FIELD_NUMBER: _ClassVar[int]
    bar_type: _common_pb2.ShortcutBar
    slot_id: int
    def __init__(self, bar_type: _Optional[_Union[_common_pb2.ShortcutBar, str]] = ..., slot_id: _Optional[int] = ...) -> None: ...

class ShortcutBarReplacedEvent(_message.Message):
    __slots__ = ("bar_type", "shortcut")
    BAR_TYPE_FIELD_NUMBER: _ClassVar[int]
    SHORTCUT_FIELD_NUMBER: _ClassVar[int]
    bar_type: _common_pb2.ShortcutBar
    shortcut: _common_pb2.Shortcut
    def __init__(self, bar_type: _Optional[_Union[_common_pb2.ShortcutBar, str]] = ..., shortcut: _Optional[_Union[_common_pb2.Shortcut, _Mapping]] = ...) -> None: ...

class StorageTab(_message.Message):
    __slots__ = ("name", "tab_number", "picto", "open_right", "drop_right", "take_right", "drop_type_limit")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TAB_NUMBER_FIELD_NUMBER: _ClassVar[int]
    PICTO_FIELD_NUMBER: _ClassVar[int]
    OPEN_RIGHT_FIELD_NUMBER: _ClassVar[int]
    DROP_RIGHT_FIELD_NUMBER: _ClassVar[int]
    TAKE_RIGHT_FIELD_NUMBER: _ClassVar[int]
    DROP_TYPE_LIMIT_FIELD_NUMBER: _ClassVar[int]
    name: str
    tab_number: int
    picto: int
    open_right: int
    drop_right: int
    take_right: int
    drop_type_limit: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, name: _Optional[str] = ..., tab_number: _Optional[int] = ..., picto: _Optional[int] = ..., open_right: _Optional[int] = ..., drop_right: _Optional[int] = ..., take_right: _Optional[int] = ..., drop_type_limit: _Optional[_Iterable[int]] = ...) -> None: ...

class MultiTabStorageEvent(_message.Message):
    __slots__ = ("tabs",)
    TABS_FIELD_NUMBER: _ClassVar[int]
    tabs: _containers.RepeatedCompositeFieldContainer[StorageTab]
    def __init__(self, tabs: _Optional[_Iterable[_Union[StorageTab, _Mapping]]] = ...) -> None: ...

class StorageInventoryContentEvent(_message.Message):
    __slots__ = ("objects", "kamas")
    OBJECTS_FIELD_NUMBER: _ClassVar[int]
    KAMAS_FIELD_NUMBER: _ClassVar[int]
    objects: _containers.RepeatedCompositeFieldContainer[_common_pb2.ObjectItemInventory]
    kamas: int
    def __init__(self, objects: _Optional[_Iterable[_Union[_common_pb2.ObjectItemInventory, _Mapping]]] = ..., kamas: _Optional[int] = ...) -> None: ...

class StorageKamasUpdateEvent(_message.Message):
    __slots__ = ("kamas",)
    KAMAS_FIELD_NUMBER: _ClassVar[int]
    kamas: int
    def __init__(self, kamas: _Optional[int] = ...) -> None: ...

class StorageObjectUpdateEvent(_message.Message):
    __slots__ = ("object",)
    OBJECT_FIELD_NUMBER: _ClassVar[int]
    object: _common_pb2.ObjectItemInventory
    def __init__(self, object: _Optional[_Union[_common_pb2.ObjectItemInventory, _Mapping]] = ...) -> None: ...

class StorageObjectsUpdateEvent(_message.Message):
    __slots__ = ("objects",)
    OBJECTS_FIELD_NUMBER: _ClassVar[int]
    objects: _containers.RepeatedCompositeFieldContainer[_common_pb2.ObjectItemInventory]
    def __init__(self, objects: _Optional[_Iterable[_Union[_common_pb2.ObjectItemInventory, _Mapping]]] = ...) -> None: ...

class StorageObjectRemovedEvent(_message.Message):
    __slots__ = ("object_uid",)
    OBJECT_UID_FIELD_NUMBER: _ClassVar[int]
    object_uid: int
    def __init__(self, object_uid: _Optional[int] = ...) -> None: ...

class StorageObjectsRemovedEvent(_message.Message):
    __slots__ = ("objects_uid",)
    OBJECTS_UID_FIELD_NUMBER: _ClassVar[int]
    objects_uid: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, objects_uid: _Optional[_Iterable[int]] = ...) -> None: ...

class SetUpdateEvent(_message.Message):
    __slots__ = ("set_id", "objects_uid", "effects")
    SET_ID_FIELD_NUMBER: _ClassVar[int]
    OBJECTS_UID_FIELD_NUMBER: _ClassVar[int]
    EFFECTS_FIELD_NUMBER: _ClassVar[int]
    set_id: int
    objects_uid: _containers.RepeatedScalarFieldContainer[int]
    effects: _containers.RepeatedCompositeFieldContainer[_common_pb2.ObjectEffect]
    def __init__(self, set_id: _Optional[int] = ..., objects_uid: _Optional[_Iterable[int]] = ..., effects: _Optional[_Iterable[_Union[_common_pb2.ObjectEffect, _Mapping]]] = ...) -> None: ...
