import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TaxCollectorUpdatesListenStartRequest(_message.Message):
    __slots__ = ("tax_collector_uid",)
    TAX_COLLECTOR_UID_FIELD_NUMBER: _ClassVar[int]
    tax_collector_uid: str
    def __init__(self, tax_collector_uid: _Optional[str] = ...) -> None: ...

class TaxCollectorUpdatesListenStopRequest(_message.Message):
    __slots__ = ("tax_collector_uid",)
    TAX_COLLECTOR_UID_FIELD_NUMBER: _ClassVar[int]
    tax_collector_uid: str
    def __init__(self, tax_collector_uid: _Optional[str] = ...) -> None: ...

class TaxCollectorOrderedSpellAddRequest(_message.Message):
    __slots__ = ("tax_collector_uid", "added_spell")
    TAX_COLLECTOR_UID_FIELD_NUMBER: _ClassVar[int]
    ADDED_SPELL_FIELD_NUMBER: _ClassVar[int]
    tax_collector_uid: str
    added_spell: _common_pb2.TaxCollectorOrderedSpell
    def __init__(self, tax_collector_uid: _Optional[str] = ..., added_spell: _Optional[_Union[_common_pb2.TaxCollectorOrderedSpell, _Mapping]] = ...) -> None: ...

class TaxCollectorOrderedSpellRemoveRequest(_message.Message):
    __slots__ = ("tax_collector_uid", "slot_id")
    TAX_COLLECTOR_UID_FIELD_NUMBER: _ClassVar[int]
    SLOT_ID_FIELD_NUMBER: _ClassVar[int]
    tax_collector_uid: str
    slot_id: int
    def __init__(self, tax_collector_uid: _Optional[str] = ..., slot_id: _Optional[int] = ...) -> None: ...

class TaxCollectorOrderedSpellMoveRequest(_message.Message):
    __slots__ = ("tax_collector_uid", "from_slot_id", "to_slot_id")
    TAX_COLLECTOR_UID_FIELD_NUMBER: _ClassVar[int]
    FROM_SLOT_ID_FIELD_NUMBER: _ClassVar[int]
    TO_SLOT_ID_FIELD_NUMBER: _ClassVar[int]
    tax_collector_uid: str
    from_slot_id: int
    to_slot_id: int
    def __init__(self, tax_collector_uid: _Optional[str] = ..., from_slot_id: _Optional[int] = ..., to_slot_id: _Optional[int] = ...) -> None: ...

class TaxCollectorPresetsUpdatesListenStartRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class TaxCollectorPresetsUpdatesListenStopRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class TaxCollectorPresetSpellAddRequest(_message.Message):
    __slots__ = ("preset_uid", "spell")
    PRESET_UID_FIELD_NUMBER: _ClassVar[int]
    SPELL_FIELD_NUMBER: _ClassVar[int]
    preset_uid: str
    spell: _common_pb2.TaxCollectorOrderedSpell
    def __init__(self, preset_uid: _Optional[str] = ..., spell: _Optional[_Union[_common_pb2.TaxCollectorOrderedSpell, _Mapping]] = ...) -> None: ...

class TaxCollectorPresetSpellRemoveRequest(_message.Message):
    __slots__ = ("preset_uid", "slot_id")
    PRESET_UID_FIELD_NUMBER: _ClassVar[int]
    SLOT_ID_FIELD_NUMBER: _ClassVar[int]
    preset_uid: str
    slot_id: int
    def __init__(self, preset_uid: _Optional[str] = ..., slot_id: _Optional[int] = ...) -> None: ...

class TaxCollectorPresetSpellMoveRequest(_message.Message):
    __slots__ = ("preset_uid", "from_slot_id", "to_slot_id")
    PRESET_UID_FIELD_NUMBER: _ClassVar[int]
    FROM_SLOT_ID_FIELD_NUMBER: _ClassVar[int]
    TO_SLOT_ID_FIELD_NUMBER: _ClassVar[int]
    preset_uid: str
    from_slot_id: int
    to_slot_id: int
    def __init__(self, preset_uid: _Optional[str] = ..., from_slot_id: _Optional[int] = ..., to_slot_id: _Optional[int] = ...) -> None: ...

class TaxCollectorTopListEvent(_message.Message):
    __slots__ = ("dungeon_tax_collectors_information", "world_tax_collectors_information")
    DUNGEON_TAX_COLLECTORS_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    WORLD_TAX_COLLECTORS_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    dungeon_tax_collectors_information: _containers.RepeatedCompositeFieldContainer[_common_pb2.TaxCollectorInformation]
    world_tax_collectors_information: _containers.RepeatedCompositeFieldContainer[_common_pb2.TaxCollectorInformation]
    def __init__(self, dungeon_tax_collectors_information: _Optional[_Iterable[_Union[_common_pb2.TaxCollectorInformation, _Mapping]]] = ..., world_tax_collectors_information: _Optional[_Iterable[_Union[_common_pb2.TaxCollectorInformation, _Mapping]]] = ...) -> None: ...

class TaxCollectorStateUpdateEvent(_message.Message):
    __slots__ = ("tax_collector_uid", "state")
    TAX_COLLECTOR_UID_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    tax_collector_uid: str
    state: _common_pb2.TaxCollectorState
    def __init__(self, tax_collector_uid: _Optional[str] = ..., state: _Optional[_Union[_common_pb2.TaxCollectorState, str]] = ...) -> None: ...

class TaxCollectorAddedEvent(_message.Message):
    __slots__ = ("caller_id", "tax_collector")
    CALLER_ID_FIELD_NUMBER: _ClassVar[int]
    TAX_COLLECTOR_FIELD_NUMBER: _ClassVar[int]
    caller_id: int
    tax_collector: _common_pb2.TaxCollectorInformation
    def __init__(self, caller_id: _Optional[int] = ..., tax_collector: _Optional[_Union[_common_pb2.TaxCollectorInformation, _Mapping]] = ...) -> None: ...

class TaxCollectorRemovedEvent(_message.Message):
    __slots__ = ("tax_collector_uid",)
    TAX_COLLECTOR_UID_FIELD_NUMBER: _ClassVar[int]
    tax_collector_uid: str
    def __init__(self, tax_collector_uid: _Optional[str] = ...) -> None: ...

class TaxCollectorAttackedEvent(_message.Message):
    __slots__ = ("first_name_id", "last_name_id", "coordinates", "alliance_uid", "alliance_tag")
    FIRST_NAME_ID_FIELD_NUMBER: _ClassVar[int]
    LAST_NAME_ID_FIELD_NUMBER: _ClassVar[int]
    COORDINATES_FIELD_NUMBER: _ClassVar[int]
    ALLIANCE_UID_FIELD_NUMBER: _ClassVar[int]
    ALLIANCE_TAG_FIELD_NUMBER: _ClassVar[int]
    first_name_id: int
    last_name_id: int
    coordinates: _common_pb2.MapExtendedCoordinates
    alliance_uid: str
    alliance_tag: str
    def __init__(self, first_name_id: _Optional[int] = ..., last_name_id: _Optional[int] = ..., coordinates: _Optional[_Union[_common_pb2.MapExtendedCoordinates, _Mapping]] = ..., alliance_uid: _Optional[str] = ..., alliance_tag: _Optional[str] = ...) -> None: ...

class TaxCollectorAttackResultEvent(_message.Message):
    __slots__ = ("dead", "first_name_id", "last_name_id", "coordinates", "alliance_uid", "alliance_tag")
    DEAD_FIELD_NUMBER: _ClassVar[int]
    FIRST_NAME_ID_FIELD_NUMBER: _ClassVar[int]
    LAST_NAME_ID_FIELD_NUMBER: _ClassVar[int]
    COORDINATES_FIELD_NUMBER: _ClassVar[int]
    ALLIANCE_UID_FIELD_NUMBER: _ClassVar[int]
    ALLIANCE_TAG_FIELD_NUMBER: _ClassVar[int]
    dead: bool
    first_name_id: int
    last_name_id: int
    coordinates: _common_pb2.MapExtendedCoordinates
    alliance_uid: str
    alliance_tag: str
    def __init__(self, dead: bool = ..., first_name_id: _Optional[int] = ..., last_name_id: _Optional[int] = ..., coordinates: _Optional[_Union[_common_pb2.MapExtendedCoordinates, _Mapping]] = ..., alliance_uid: _Optional[str] = ..., alliance_tag: _Optional[str] = ...) -> None: ...

class TaxCollectorHarvestedEvent(_message.Message):
    __slots__ = ("tax_collector_uid", "harvester_id", "harvester_name")
    TAX_COLLECTOR_UID_FIELD_NUMBER: _ClassVar[int]
    HARVESTER_ID_FIELD_NUMBER: _ClassVar[int]
    HARVESTER_NAME_FIELD_NUMBER: _ClassVar[int]
    tax_collector_uid: str
    harvester_id: int
    harvester_name: str
    def __init__(self, tax_collector_uid: _Optional[str] = ..., harvester_id: _Optional[int] = ..., harvester_name: _Optional[str] = ...) -> None: ...

class TaxCollectorMovement(_message.Message):
    __slots__ = ("movement_type", "first_name_id", "last_name_id", "coordinates", "player_id", "player_name")
    class TaxCollectorMovementType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TAX_COLLECTOR_UNKNOWN_ACTION: _ClassVar[TaxCollectorMovement.TaxCollectorMovementType]
        TAX_COLLECTOR_HIRED: _ClassVar[TaxCollectorMovement.TaxCollectorMovementType]
        TAX_COLLECTOR_HARVESTED: _ClassVar[TaxCollectorMovement.TaxCollectorMovementType]
        TAX_COLLECTOR_DEFEATED: _ClassVar[TaxCollectorMovement.TaxCollectorMovementType]
        TAX_COLLECTOR_DESTROYED: _ClassVar[TaxCollectorMovement.TaxCollectorMovementType]
    TAX_COLLECTOR_UNKNOWN_ACTION: TaxCollectorMovement.TaxCollectorMovementType
    TAX_COLLECTOR_HIRED: TaxCollectorMovement.TaxCollectorMovementType
    TAX_COLLECTOR_HARVESTED: TaxCollectorMovement.TaxCollectorMovementType
    TAX_COLLECTOR_DEFEATED: TaxCollectorMovement.TaxCollectorMovementType
    TAX_COLLECTOR_DESTROYED: TaxCollectorMovement.TaxCollectorMovementType
    MOVEMENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    FIRST_NAME_ID_FIELD_NUMBER: _ClassVar[int]
    LAST_NAME_ID_FIELD_NUMBER: _ClassVar[int]
    COORDINATES_FIELD_NUMBER: _ClassVar[int]
    PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
    PLAYER_NAME_FIELD_NUMBER: _ClassVar[int]
    movement_type: TaxCollectorMovement.TaxCollectorMovementType
    first_name_id: int
    last_name_id: int
    coordinates: _common_pb2.MapExtendedCoordinates
    player_id: int
    player_name: str
    def __init__(self, movement_type: _Optional[_Union[TaxCollectorMovement.TaxCollectorMovementType, str]] = ..., first_name_id: _Optional[int] = ..., last_name_id: _Optional[int] = ..., coordinates: _Optional[_Union[_common_pb2.MapExtendedCoordinates, _Mapping]] = ..., player_id: _Optional[int] = ..., player_name: _Optional[str] = ...) -> None: ...

class TaxCollectorMovementsOfflineEvent(_message.Message):
    __slots__ = ("movements",)
    MOVEMENTS_FIELD_NUMBER: _ClassVar[int]
    movements: _containers.RepeatedCompositeFieldContainer[TaxCollectorMovement]
    def __init__(self, movements: _Optional[_Iterable[_Union[TaxCollectorMovement, _Mapping]]] = ...) -> None: ...

class TaxCollectorEquipmentUpdateEvent(_message.Message):
    __slots__ = ("tax_collector_uid", "object", "added", "characteristics")
    TAX_COLLECTOR_UID_FIELD_NUMBER: _ClassVar[int]
    OBJECT_FIELD_NUMBER: _ClassVar[int]
    ADDED_FIELD_NUMBER: _ClassVar[int]
    CHARACTERISTICS_FIELD_NUMBER: _ClassVar[int]
    tax_collector_uid: str
    object: _common_pb2.ObjectItemInventory
    added: bool
    characteristics: _containers.RepeatedCompositeFieldContainer[_common_pb2.CharacterCharacteristic]
    def __init__(self, tax_collector_uid: _Optional[str] = ..., object: _Optional[_Union[_common_pb2.ObjectItemInventory, _Mapping]] = ..., added: bool = ..., characteristics: _Optional[_Iterable[_Union[_common_pb2.CharacterCharacteristic, _Mapping]]] = ...) -> None: ...

class TaxCollectorErrorEvent(_message.Message):
    __slots__ = ("reason",)
    class TaxCollectorErrorReason(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TAX_COLLECTOR_ERROR_UNKNOWN: _ClassVar[TaxCollectorErrorEvent.TaxCollectorErrorReason]
        TAX_COLLECTOR_NOT_FOUND: _ClassVar[TaxCollectorErrorEvent.TaxCollectorErrorReason]
        TAX_COLLECTOR_NOT_OWNED: _ClassVar[TaxCollectorErrorEvent.TaxCollectorErrorReason]
        TAX_COLLECTOR_NO_RIGHTS: _ClassVar[TaxCollectorErrorEvent.TaxCollectorErrorReason]
        TAX_COLLECTOR_MAX_REACHED: _ClassVar[TaxCollectorErrorEvent.TaxCollectorErrorReason]
        TAX_COLLECTOR_ALREADY_ONE: _ClassVar[TaxCollectorErrorEvent.TaxCollectorErrorReason]
        TAX_COLLECTOR_CANT_HIRE_YET: _ClassVar[TaxCollectorErrorEvent.TaxCollectorErrorReason]
        TAX_COLLECTOR_CANT_HIRE_HERE: _ClassVar[TaxCollectorErrorEvent.TaxCollectorErrorReason]
        TAX_COLLECTOR_NOT_ENOUGH_KAMAS: _ClassVar[TaxCollectorErrorEvent.TaxCollectorErrorReason]
    TAX_COLLECTOR_ERROR_UNKNOWN: TaxCollectorErrorEvent.TaxCollectorErrorReason
    TAX_COLLECTOR_NOT_FOUND: TaxCollectorErrorEvent.TaxCollectorErrorReason
    TAX_COLLECTOR_NOT_OWNED: TaxCollectorErrorEvent.TaxCollectorErrorReason
    TAX_COLLECTOR_NO_RIGHTS: TaxCollectorErrorEvent.TaxCollectorErrorReason
    TAX_COLLECTOR_MAX_REACHED: TaxCollectorErrorEvent.TaxCollectorErrorReason
    TAX_COLLECTOR_ALREADY_ONE: TaxCollectorErrorEvent.TaxCollectorErrorReason
    TAX_COLLECTOR_CANT_HIRE_YET: TaxCollectorErrorEvent.TaxCollectorErrorReason
    TAX_COLLECTOR_CANT_HIRE_HERE: TaxCollectorErrorEvent.TaxCollectorErrorReason
    TAX_COLLECTOR_NOT_ENOUGH_KAMAS: TaxCollectorErrorEvent.TaxCollectorErrorReason
    REASON_FIELD_NUMBER: _ClassVar[int]
    reason: TaxCollectorErrorEvent.TaxCollectorErrorReason
    def __init__(self, reason: _Optional[_Union[TaxCollectorErrorEvent.TaxCollectorErrorReason, str]] = ...) -> None: ...

class TaxCollectorUpdatesListeningConfirmationEvent(_message.Message):
    __slots__ = ("information",)
    INFORMATION_FIELD_NUMBER: _ClassVar[int]
    information: _common_pb2.TaxCollectorInformation
    def __init__(self, information: _Optional[_Union[_common_pb2.TaxCollectorInformation, _Mapping]] = ...) -> None: ...

class TaxCollectorOrderedSpellUpdatedEvent(_message.Message):
    __slots__ = ("tax_collector_uid", "spells")
    TAX_COLLECTOR_UID_FIELD_NUMBER: _ClassVar[int]
    SPELLS_FIELD_NUMBER: _ClassVar[int]
    tax_collector_uid: str
    spells: _containers.RepeatedCompositeFieldContainer[_common_pb2.TaxCollectorOrderedSpell]
    def __init__(self, tax_collector_uid: _Optional[str] = ..., spells: _Optional[_Iterable[_Union[_common_pb2.TaxCollectorOrderedSpell, _Mapping]]] = ...) -> None: ...

class TaxCollectorPresetsEvent(_message.Message):
    __slots__ = ("presets",)
    PRESETS_FIELD_NUMBER: _ClassVar[int]
    presets: _containers.RepeatedCompositeFieldContainer[_common_pb2.TaxCollectorPreset]
    def __init__(self, presets: _Optional[_Iterable[_Union[_common_pb2.TaxCollectorPreset, _Mapping]]] = ...) -> None: ...

class TaxCollectorPresetSpellUpdatedEvent(_message.Message):
    __slots__ = ("preset_uid", "spells")
    PRESET_UID_FIELD_NUMBER: _ClassVar[int]
    SPELLS_FIELD_NUMBER: _ClassVar[int]
    preset_uid: str
    spells: _containers.RepeatedCompositeFieldContainer[_common_pb2.TaxCollectorOrderedSpell]
    def __init__(self, preset_uid: _Optional[str] = ..., spells: _Optional[_Iterable[_Union[_common_pb2.TaxCollectorOrderedSpell, _Mapping]]] = ...) -> None: ...

class TaxCollectorFightRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
