from com.ankama.dofus.server.game.protocol import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CharacterPresetInfo(_message.Message):
    __slots__ = ("uuid", "name", "symbol_id", "is_favorite", "last_modification_date", "equipment_by_position", "spell_preset", "characteristics_info", "preset_look", "ride", "outfit_uuid")
    class EquipmentByPositionEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: Equipment
        def __init__(self, key: _Optional[int] = ..., value: _Optional[_Union[Equipment, _Mapping]] = ...) -> None: ...
    UUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    SYMBOL_ID_FIELD_NUMBER: _ClassVar[int]
    IS_FAVORITE_FIELD_NUMBER: _ClassVar[int]
    LAST_MODIFICATION_DATE_FIELD_NUMBER: _ClassVar[int]
    EQUIPMENT_BY_POSITION_FIELD_NUMBER: _ClassVar[int]
    SPELL_PRESET_FIELD_NUMBER: _ClassVar[int]
    CHARACTERISTICS_INFO_FIELD_NUMBER: _ClassVar[int]
    PRESET_LOOK_FIELD_NUMBER: _ClassVar[int]
    RIDE_FIELD_NUMBER: _ClassVar[int]
    OUTFIT_UUID_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    name: str
    symbol_id: int
    is_favorite: bool
    last_modification_date: str
    equipment_by_position: _containers.RepeatedCompositeFieldContainer[CharacterPresetInfo.EquipmentByPositionEntry]
    spell_preset: SpellPreset
    characteristics_info: CharacteristicsInfo
    preset_look: PresetLook
    ride: Ride
    outfit_uuid: str
    def __init__(self, uuid: _Optional[str] = ..., name: _Optional[str] = ..., symbol_id: _Optional[int] = ..., is_favorite: bool = ..., last_modification_date: _Optional[str] = ..., equipment_by_position: _Optional[_Iterable[_Union[CharacterPresetInfo.EquipmentByPositionEntry, _Mapping]]] = ..., spell_preset: _Optional[_Union[SpellPreset, _Mapping]] = ..., characteristics_info: _Optional[_Union[CharacteristicsInfo, _Mapping]] = ..., preset_look: _Optional[_Union[PresetLook, _Mapping]] = ..., ride: _Optional[_Union[Ride, _Mapping]] = ..., outfit_uuid: _Optional[str] = ...) -> None: ...

class ForgettableSpellPresetInfo(_message.Message):
    __slots__ = ("uuid", "name", "symbol_id", "is_favorite", "last_modification_date", "spell_preset", "forgettable_spell_info_by_id")
    class ForgettableSpellInfoByIdEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: ForgettableSpellInfo
        def __init__(self, key: _Optional[int] = ..., value: _Optional[_Union[ForgettableSpellInfo, _Mapping]] = ...) -> None: ...
    UUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    SYMBOL_ID_FIELD_NUMBER: _ClassVar[int]
    IS_FAVORITE_FIELD_NUMBER: _ClassVar[int]
    LAST_MODIFICATION_DATE_FIELD_NUMBER: _ClassVar[int]
    SPELL_PRESET_FIELD_NUMBER: _ClassVar[int]
    FORGETTABLE_SPELL_INFO_BY_ID_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    name: str
    symbol_id: int
    is_favorite: bool
    last_modification_date: str
    spell_preset: SpellPreset
    forgettable_spell_info_by_id: _containers.RepeatedCompositeFieldContainer[ForgettableSpellPresetInfo.ForgettableSpellInfoByIdEntry]
    def __init__(self, uuid: _Optional[str] = ..., name: _Optional[str] = ..., symbol_id: _Optional[int] = ..., is_favorite: bool = ..., last_modification_date: _Optional[str] = ..., spell_preset: _Optional[_Union[SpellPreset, _Mapping]] = ..., forgettable_spell_info_by_id: _Optional[_Iterable[_Union[ForgettableSpellPresetInfo.ForgettableSpellInfoByIdEntry, _Mapping]]] = ...) -> None: ...

class PresetLook(_message.Message):
    __slots__ = ("look_with_outfit", "look_without_outfit")
    LOOK_WITH_OUTFIT_FIELD_NUMBER: _ClassVar[int]
    LOOK_WITHOUT_OUTFIT_FIELD_NUMBER: _ClassVar[int]
    look_with_outfit: _common_pb2.EntityLook
    look_without_outfit: _common_pb2.EntityLook
    def __init__(self, look_with_outfit: _Optional[_Union[_common_pb2.EntityLook, _Mapping]] = ..., look_without_outfit: _Optional[_Union[_common_pb2.EntityLook, _Mapping]] = ...) -> None: ...

class CharacteristicsInfo(_message.Message):
    __slots__ = ("characteristic_details_by_id",)
    class CharacteristicDetailsByIdEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: CharacteristicsInfo.CharacteristicsDetails
        def __init__(self, key: _Optional[int] = ..., value: _Optional[_Union[CharacteristicsInfo.CharacteristicsDetails, _Mapping]] = ...) -> None: ...
    class CharacteristicsDetails(_message.Message):
        __slots__ = ("limit", "from_base", "from_allocated", "from_equipment", "from_bonus", "from_initial_bonus")
        LIMIT_FIELD_NUMBER: _ClassVar[int]
        FROM_BASE_FIELD_NUMBER: _ClassVar[int]
        FROM_ALLOCATED_FIELD_NUMBER: _ClassVar[int]
        FROM_EQUIPMENT_FIELD_NUMBER: _ClassVar[int]
        FROM_BONUS_FIELD_NUMBER: _ClassVar[int]
        FROM_INITIAL_BONUS_FIELD_NUMBER: _ClassVar[int]
        limit: int
        from_base: int
        from_allocated: int
        from_equipment: int
        from_bonus: int
        from_initial_bonus: int
        def __init__(self, limit: _Optional[int] = ..., from_base: _Optional[int] = ..., from_allocated: _Optional[int] = ..., from_equipment: _Optional[int] = ..., from_bonus: _Optional[int] = ..., from_initial_bonus: _Optional[int] = ...) -> None: ...
    CHARACTERISTIC_DETAILS_BY_ID_FIELD_NUMBER: _ClassVar[int]
    characteristic_details_by_id: _containers.RepeatedCompositeFieldContainer[CharacteristicsInfo.CharacteristicDetailsByIdEntry]
    def __init__(self, characteristic_details_by_id: _Optional[_Iterable[_Union[CharacteristicsInfo.CharacteristicDetailsByIdEntry, _Mapping]]] = ...) -> None: ...

class Equipment(_message.Message):
    __slots__ = ("gid", "uid", "effects")
    GID_FIELD_NUMBER: _ClassVar[int]
    UID_FIELD_NUMBER: _ClassVar[int]
    EFFECTS_FIELD_NUMBER: _ClassVar[int]
    gid: int
    uid: int
    effects: _containers.RepeatedCompositeFieldContainer[_common_pb2.ObjectEffect]
    def __init__(self, gid: _Optional[int] = ..., uid: _Optional[int] = ..., effects: _Optional[_Iterable[_Union[_common_pb2.ObjectEffect, _Mapping]]] = ...) -> None: ...

class Ride(_message.Message):
    __slots__ = ("model_id", "level", "is_current_ride")
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    LEVEL_FIELD_NUMBER: _ClassVar[int]
    IS_CURRENT_RIDE_FIELD_NUMBER: _ClassVar[int]
    model_id: int
    level: int
    is_current_ride: bool
    def __init__(self, model_id: _Optional[int] = ..., level: _Optional[int] = ..., is_current_ride: bool = ...) -> None: ...

class SpellPositions(_message.Message):
    __slots__ = ("positions",)
    POSITIONS_FIELD_NUMBER: _ClassVar[int]
    positions: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, positions: _Optional[_Iterable[int]] = ...) -> None: ...

class ForgettableSpellInfo(_message.Message):
    __slots__ = ("spell_positions", "is_missing")
    SPELL_POSITIONS_FIELD_NUMBER: _ClassVar[int]
    IS_MISSING_FIELD_NUMBER: _ClassVar[int]
    spell_positions: SpellPositions
    is_missing: bool
    def __init__(self, spell_positions: _Optional[_Union[SpellPositions, _Mapping]] = ..., is_missing: bool = ...) -> None: ...

class SpellPreset(_message.Message):
    __slots__ = ("spell_positions_by_id",)
    class SpellPositionsByIdEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: SpellPositions
        def __init__(self, key: _Optional[int] = ..., value: _Optional[_Union[SpellPositions, _Mapping]] = ...) -> None: ...
    SPELL_POSITIONS_BY_ID_FIELD_NUMBER: _ClassVar[int]
    spell_positions_by_id: _containers.RepeatedCompositeFieldContainer[SpellPreset.SpellPositionsByIdEntry]
    def __init__(self, spell_positions_by_id: _Optional[_Iterable[_Union[SpellPreset.SpellPositionsByIdEntry, _Mapping]]] = ...) -> None: ...

class PresetOrigin(_message.Message):
    __slots__ = ("empty", "player", "clone")
    class EmptyPreset(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class PlayerCopy(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class PresetClone(_message.Message):
        __slots__ = ("preset_uuid_to_clone",)
        PRESET_UUID_TO_CLONE_FIELD_NUMBER: _ClassVar[int]
        preset_uuid_to_clone: str
        def __init__(self, preset_uuid_to_clone: _Optional[str] = ...) -> None: ...
    EMPTY_FIELD_NUMBER: _ClassVar[int]
    PLAYER_FIELD_NUMBER: _ClassVar[int]
    CLONE_FIELD_NUMBER: _ClassVar[int]
    empty: PresetOrigin.EmptyPreset
    player: PresetOrigin.PlayerCopy
    clone: PresetOrigin.PresetClone
    def __init__(self, empty: _Optional[_Union[PresetOrigin.EmptyPreset, _Mapping]] = ..., player: _Optional[_Union[PresetOrigin.PlayerCopy, _Mapping]] = ..., clone: _Optional[_Union[PresetOrigin.PresetClone, _Mapping]] = ...) -> None: ...

class CharacterPresetCreateRequest(_message.Message):
    __slots__ = ("name", "symbol_id", "origin")
    NAME_FIELD_NUMBER: _ClassVar[int]
    SYMBOL_ID_FIELD_NUMBER: _ClassVar[int]
    ORIGIN_FIELD_NUMBER: _ClassVar[int]
    name: str
    symbol_id: int
    origin: PresetOrigin
    def __init__(self, name: _Optional[str] = ..., symbol_id: _Optional[int] = ..., origin: _Optional[_Union[PresetOrigin, _Mapping]] = ...) -> None: ...

class CharacterPresetCreateResponse(_message.Message):
    __slots__ = ("success", "error")
    class Error(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        MAX_QUANTITY: _ClassVar[CharacterPresetCreateResponse.Error]
        INVALID_NAME_SIZE: _ClassVar[CharacterPresetCreateResponse.Error]
        PRESET_NOT_FOUND: _ClassVar[CharacterPresetCreateResponse.Error]
        UNKNOWN: _ClassVar[CharacterPresetCreateResponse.Error]
    MAX_QUANTITY: CharacterPresetCreateResponse.Error
    INVALID_NAME_SIZE: CharacterPresetCreateResponse.Error
    PRESET_NOT_FOUND: CharacterPresetCreateResponse.Error
    UNKNOWN: CharacterPresetCreateResponse.Error
    class Success(_message.Message):
        __slots__ = ("preset_info",)
        PRESET_INFO_FIELD_NUMBER: _ClassVar[int]
        preset_info: CharacterPresetInfo
        def __init__(self, preset_info: _Optional[_Union[CharacterPresetInfo, _Mapping]] = ...) -> None: ...
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: CharacterPresetCreateResponse.Success
    error: CharacterPresetCreateResponse.Error
    def __init__(self, success: _Optional[_Union[CharacterPresetCreateResponse.Success, _Mapping]] = ..., error: _Optional[_Union[CharacterPresetCreateResponse.Error, str]] = ...) -> None: ...

class ForgettableSpellPresetCreateRequest(_message.Message):
    __slots__ = ("name", "symbol_id", "origin")
    NAME_FIELD_NUMBER: _ClassVar[int]
    SYMBOL_ID_FIELD_NUMBER: _ClassVar[int]
    ORIGIN_FIELD_NUMBER: _ClassVar[int]
    name: str
    symbol_id: int
    origin: PresetOrigin
    def __init__(self, name: _Optional[str] = ..., symbol_id: _Optional[int] = ..., origin: _Optional[_Union[PresetOrigin, _Mapping]] = ...) -> None: ...

class ForgettableSpellPresetCreateResponse(_message.Message):
    __slots__ = ("success", "error")
    class Error(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        FEATURE_DISABLED: _ClassVar[ForgettableSpellPresetCreateResponse.Error]
        MAX_QUANTITY: _ClassVar[ForgettableSpellPresetCreateResponse.Error]
        INVALID_NAME_SIZE: _ClassVar[ForgettableSpellPresetCreateResponse.Error]
        PRESET_NOT_FOUND: _ClassVar[ForgettableSpellPresetCreateResponse.Error]
        UNKNOWN: _ClassVar[ForgettableSpellPresetCreateResponse.Error]
    FEATURE_DISABLED: ForgettableSpellPresetCreateResponse.Error
    MAX_QUANTITY: ForgettableSpellPresetCreateResponse.Error
    INVALID_NAME_SIZE: ForgettableSpellPresetCreateResponse.Error
    PRESET_NOT_FOUND: ForgettableSpellPresetCreateResponse.Error
    UNKNOWN: ForgettableSpellPresetCreateResponse.Error
    class Success(_message.Message):
        __slots__ = ("preset_info",)
        PRESET_INFO_FIELD_NUMBER: _ClassVar[int]
        preset_info: ForgettableSpellPresetInfo
        def __init__(self, preset_info: _Optional[_Union[ForgettableSpellPresetInfo, _Mapping]] = ...) -> None: ...
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: ForgettableSpellPresetCreateResponse.Success
    error: ForgettableSpellPresetCreateResponse.Error
    def __init__(self, success: _Optional[_Union[ForgettableSpellPresetCreateResponse.Success, _Mapping]] = ..., error: _Optional[_Union[ForgettableSpellPresetCreateResponse.Error, str]] = ...) -> None: ...

class CharacterPresetSetRequest(_message.Message):
    __slots__ = ("uuid", "origin")
    UUID_FIELD_NUMBER: _ClassVar[int]
    ORIGIN_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    origin: PresetOrigin
    def __init__(self, uuid: _Optional[str] = ..., origin: _Optional[_Union[PresetOrigin, _Mapping]] = ...) -> None: ...

class CharacterPresetSetResponse(_message.Message):
    __slots__ = ("is_success", "preset_info")
    IS_SUCCESS_FIELD_NUMBER: _ClassVar[int]
    PRESET_INFO_FIELD_NUMBER: _ClassVar[int]
    is_success: bool
    preset_info: CharacterPresetInfo
    def __init__(self, is_success: bool = ..., preset_info: _Optional[_Union[CharacterPresetInfo, _Mapping]] = ...) -> None: ...

class ForgettableSpellPresetSetRequest(_message.Message):
    __slots__ = ("uuid", "origin")
    UUID_FIELD_NUMBER: _ClassVar[int]
    ORIGIN_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    origin: PresetOrigin
    def __init__(self, uuid: _Optional[str] = ..., origin: _Optional[_Union[PresetOrigin, _Mapping]] = ...) -> None: ...

class ForgettableSpellPresetSetResponse(_message.Message):
    __slots__ = ("is_success", "preset_info")
    IS_SUCCESS_FIELD_NUMBER: _ClassVar[int]
    PRESET_INFO_FIELD_NUMBER: _ClassVar[int]
    is_success: bool
    preset_info: ForgettableSpellPresetInfo
    def __init__(self, is_success: bool = ..., preset_info: _Optional[_Union[ForgettableSpellPresetInfo, _Mapping]] = ...) -> None: ...

class PresetSaveRequest(_message.Message):
    __slots__ = ("type", "uuid")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    UUID_FIELD_NUMBER: _ClassVar[int]
    type: _common_pb2.PresetType
    uuid: str
    def __init__(self, type: _Optional[_Union[_common_pb2.PresetType, str]] = ..., uuid: _Optional[str] = ...) -> None: ...

class PresetSaveResponse(_message.Message):
    __slots__ = ("is_success",)
    IS_SUCCESS_FIELD_NUMBER: _ClassVar[int]
    is_success: bool
    def __init__(self, is_success: bool = ...) -> None: ...

class CharacterPresetResetRequest(_message.Message):
    __slots__ = ("uuid",)
    UUID_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    def __init__(self, uuid: _Optional[str] = ...) -> None: ...

class CharacterPresetResetResponse(_message.Message):
    __slots__ = ("is_success", "preset_info")
    IS_SUCCESS_FIELD_NUMBER: _ClassVar[int]
    PRESET_INFO_FIELD_NUMBER: _ClassVar[int]
    is_success: bool
    preset_info: CharacterPresetInfo
    def __init__(self, is_success: bool = ..., preset_info: _Optional[_Union[CharacterPresetInfo, _Mapping]] = ...) -> None: ...

class ForgettableSpellPresetResetRequest(_message.Message):
    __slots__ = ("uuid",)
    UUID_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    def __init__(self, uuid: _Optional[str] = ...) -> None: ...

class ForgettableSpellPresetResetResponse(_message.Message):
    __slots__ = ("is_success", "preset_info")
    IS_SUCCESS_FIELD_NUMBER: _ClassVar[int]
    PRESET_INFO_FIELD_NUMBER: _ClassVar[int]
    is_success: bool
    preset_info: ForgettableSpellPresetInfo
    def __init__(self, is_success: bool = ..., preset_info: _Optional[_Union[ForgettableSpellPresetInfo, _Mapping]] = ...) -> None: ...

class PresetDeleteRequest(_message.Message):
    __slots__ = ("preset_uuid", "preset_type")
    PRESET_UUID_FIELD_NUMBER: _ClassVar[int]
    PRESET_TYPE_FIELD_NUMBER: _ClassVar[int]
    preset_uuid: str
    preset_type: _common_pb2.PresetType
    def __init__(self, preset_uuid: _Optional[str] = ..., preset_type: _Optional[_Union[_common_pb2.PresetType, str]] = ...) -> None: ...

class PresetDeleteResponse(_message.Message):
    __slots__ = ("is_success",)
    IS_SUCCESS_FIELD_NUMBER: _ClassVar[int]
    is_success: bool
    def __init__(self, is_success: bool = ...) -> None: ...

class PresetUseRequest(_message.Message):
    __slots__ = ("preset_uuid", "preset_type")
    PRESET_UUID_FIELD_NUMBER: _ClassVar[int]
    PRESET_TYPE_FIELD_NUMBER: _ClassVar[int]
    preset_uuid: str
    preset_type: _common_pb2.PresetType
    def __init__(self, preset_uuid: _Optional[str] = ..., preset_type: _Optional[_Union[_common_pb2.PresetType, str]] = ...) -> None: ...

class PresetUseResponse(_message.Message):
    __slots__ = ("result_enum", "missing_equipments")
    class ResultEnum(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        OK: _ClassVar[PresetUseResponse.ResultEnum]
        ERROR_COOLDOWN: _ClassVar[PresetUseResponse.ResultEnum]
        ERROR_BAD_PRESET_UUID: _ClassVar[PresetUseResponse.ResultEnum]
        ERROR_INVALID_STATE: _ClassVar[PresetUseResponse.ResultEnum]
        ERROR_UNKNOWN: _ClassVar[PresetUseResponse.ResultEnum]
        ERROR_INVALID_DATA: _ClassVar[PresetUseResponse.ResultEnum]
        MISSING_SPELLS: _ClassVar[PresetUseResponse.ResultEnum]
    OK: PresetUseResponse.ResultEnum
    ERROR_COOLDOWN: PresetUseResponse.ResultEnum
    ERROR_BAD_PRESET_UUID: PresetUseResponse.ResultEnum
    ERROR_INVALID_STATE: PresetUseResponse.ResultEnum
    ERROR_UNKNOWN: PresetUseResponse.ResultEnum
    ERROR_INVALID_DATA: PresetUseResponse.ResultEnum
    MISSING_SPELLS: PresetUseResponse.ResultEnum
    class MissingEquipments(_message.Message):
        __slots__ = ("missing_item_gids", "missing_ride_model_id")
        MISSING_ITEM_GIDS_FIELD_NUMBER: _ClassVar[int]
        MISSING_RIDE_MODEL_ID_FIELD_NUMBER: _ClassVar[int]
        missing_item_gids: _containers.RepeatedScalarFieldContainer[int]
        missing_ride_model_id: int
        def __init__(self, missing_item_gids: _Optional[_Iterable[int]] = ..., missing_ride_model_id: _Optional[int] = ...) -> None: ...
    RESULT_ENUM_FIELD_NUMBER: _ClassVar[int]
    MISSING_EQUIPMENTS_FIELD_NUMBER: _ClassVar[int]
    result_enum: PresetUseResponse.ResultEnum
    missing_equipments: PresetUseResponse.MissingEquipments
    def __init__(self, result_enum: _Optional[_Union[PresetUseResponse.ResultEnum, str]] = ..., missing_equipments: _Optional[_Union[PresetUseResponse.MissingEquipments, _Mapping]] = ...) -> None: ...

class PresetSpellUpdateRequest(_message.Message):
    __slots__ = ("preset_uuid", "target", "spell_preset")
    class Target(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        CHARACTER: _ClassVar[PresetSpellUpdateRequest.Target]
        FORGETTABLE_BASE: _ClassVar[PresetSpellUpdateRequest.Target]
        FORGETTABLE_SPELL: _ClassVar[PresetSpellUpdateRequest.Target]
    CHARACTER: PresetSpellUpdateRequest.Target
    FORGETTABLE_BASE: PresetSpellUpdateRequest.Target
    FORGETTABLE_SPELL: PresetSpellUpdateRequest.Target
    PRESET_UUID_FIELD_NUMBER: _ClassVar[int]
    TARGET_FIELD_NUMBER: _ClassVar[int]
    SPELL_PRESET_FIELD_NUMBER: _ClassVar[int]
    preset_uuid: str
    target: PresetSpellUpdateRequest.Target
    spell_preset: SpellPreset
    def __init__(self, preset_uuid: _Optional[str] = ..., target: _Optional[_Union[PresetSpellUpdateRequest.Target, str]] = ..., spell_preset: _Optional[_Union[SpellPreset, _Mapping]] = ...) -> None: ...

class PresetSpellUpdateResponse(_message.Message):
    __slots__ = ("is_success",)
    IS_SUCCESS_FIELD_NUMBER: _ClassVar[int]
    is_success: bool
    def __init__(self, is_success: bool = ...) -> None: ...

class PresetStatUpdateRequest(_message.Message):
    __slots__ = ("preset_uuid", "stat_by_id")
    class StatByIdEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: int
        def __init__(self, key: _Optional[int] = ..., value: _Optional[int] = ...) -> None: ...
    PRESET_UUID_FIELD_NUMBER: _ClassVar[int]
    STAT_BY_ID_FIELD_NUMBER: _ClassVar[int]
    preset_uuid: str
    stat_by_id: _containers.RepeatedCompositeFieldContainer[PresetStatUpdateRequest.StatByIdEntry]
    def __init__(self, preset_uuid: _Optional[str] = ..., stat_by_id: _Optional[_Iterable[_Union[PresetStatUpdateRequest.StatByIdEntry, _Mapping]]] = ...) -> None: ...

class PresetStatUpdateResponse(_message.Message):
    __slots__ = ("is_success", "characteristics_info")
    IS_SUCCESS_FIELD_NUMBER: _ClassVar[int]
    CHARACTERISTICS_INFO_FIELD_NUMBER: _ClassVar[int]
    is_success: bool
    characteristics_info: CharacteristicsInfo
    def __init__(self, is_success: bool = ..., characteristics_info: _Optional[_Union[CharacteristicsInfo, _Mapping]] = ...) -> None: ...

class PresetEquipmentUpdateRequest(_message.Message):
    __slots__ = ("character_preset_uuid", "set_item", "remove_item", "set_ride", "remove_ride")
    class SetItem(_message.Message):
        __slots__ = ("position", "item_uid")
        POSITION_FIELD_NUMBER: _ClassVar[int]
        ITEM_UID_FIELD_NUMBER: _ClassVar[int]
        position: int
        item_uid: int
        def __init__(self, position: _Optional[int] = ..., item_uid: _Optional[int] = ...) -> None: ...
    class RemoveItem(_message.Message):
        __slots__ = ("position",)
        POSITION_FIELD_NUMBER: _ClassVar[int]
        position: int
        def __init__(self, position: _Optional[int] = ...) -> None: ...
    class SetRide(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class RemoveRide(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    CHARACTER_PRESET_UUID_FIELD_NUMBER: _ClassVar[int]
    SET_ITEM_FIELD_NUMBER: _ClassVar[int]
    REMOVE_ITEM_FIELD_NUMBER: _ClassVar[int]
    SET_RIDE_FIELD_NUMBER: _ClassVar[int]
    REMOVE_RIDE_FIELD_NUMBER: _ClassVar[int]
    character_preset_uuid: str
    set_item: PresetEquipmentUpdateRequest.SetItem
    remove_item: PresetEquipmentUpdateRequest.RemoveItem
    set_ride: PresetEquipmentUpdateRequest.SetRide
    remove_ride: PresetEquipmentUpdateRequest.RemoveRide
    def __init__(self, character_preset_uuid: _Optional[str] = ..., set_item: _Optional[_Union[PresetEquipmentUpdateRequest.SetItem, _Mapping]] = ..., remove_item: _Optional[_Union[PresetEquipmentUpdateRequest.RemoveItem, _Mapping]] = ..., set_ride: _Optional[_Union[PresetEquipmentUpdateRequest.SetRide, _Mapping]] = ..., remove_ride: _Optional[_Union[PresetEquipmentUpdateRequest.RemoveRide, _Mapping]] = ...) -> None: ...

class PresetEquipmentUpdateResponse(_message.Message):
    __slots__ = ("is_success", "equipment_refresh")
    class EquipmentRefresh(_message.Message):
        __slots__ = ("characteristics_info", "preset_look")
        CHARACTERISTICS_INFO_FIELD_NUMBER: _ClassVar[int]
        PRESET_LOOK_FIELD_NUMBER: _ClassVar[int]
        characteristics_info: CharacteristicsInfo
        preset_look: PresetLook
        def __init__(self, characteristics_info: _Optional[_Union[CharacteristicsInfo, _Mapping]] = ..., preset_look: _Optional[_Union[PresetLook, _Mapping]] = ...) -> None: ...
    IS_SUCCESS_FIELD_NUMBER: _ClassVar[int]
    EQUIPMENT_REFRESH_FIELD_NUMBER: _ClassVar[int]
    is_success: bool
    equipment_refresh: PresetEquipmentUpdateResponse.EquipmentRefresh
    def __init__(self, is_success: bool = ..., equipment_refresh: _Optional[_Union[PresetEquipmentUpdateResponse.EquipmentRefresh, _Mapping]] = ...) -> None: ...

class PresetRenameRequest(_message.Message):
    __slots__ = ("preset_uuid", "preset_type", "name")
    PRESET_UUID_FIELD_NUMBER: _ClassVar[int]
    PRESET_TYPE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    preset_uuid: str
    preset_type: _common_pb2.PresetType
    name: str
    def __init__(self, preset_uuid: _Optional[str] = ..., preset_type: _Optional[_Union[_common_pb2.PresetType, str]] = ..., name: _Optional[str] = ...) -> None: ...

class PresetRenameResponse(_message.Message):
    __slots__ = ("result",)
    class Result(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SUCCESS: _ClassVar[PresetRenameResponse.Result]
        PRESET_NOT_FOUND: _ClassVar[PresetRenameResponse.Result]
        ERROR_NAME_SIZE: _ClassVar[PresetRenameResponse.Result]
        UNKNOWN_ERROR: _ClassVar[PresetRenameResponse.Result]
        FEATURE_DISABLED: _ClassVar[PresetRenameResponse.Result]
    SUCCESS: PresetRenameResponse.Result
    PRESET_NOT_FOUND: PresetRenameResponse.Result
    ERROR_NAME_SIZE: PresetRenameResponse.Result
    UNKNOWN_ERROR: PresetRenameResponse.Result
    FEATURE_DISABLED: PresetRenameResponse.Result
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: PresetRenameResponse.Result
    def __init__(self, result: _Optional[_Union[PresetRenameResponse.Result, str]] = ...) -> None: ...

class PresetSymbolUpdateRequest(_message.Message):
    __slots__ = ("preset_uuid", "preset_type", "symbol_id")
    PRESET_UUID_FIELD_NUMBER: _ClassVar[int]
    PRESET_TYPE_FIELD_NUMBER: _ClassVar[int]
    SYMBOL_ID_FIELD_NUMBER: _ClassVar[int]
    preset_uuid: str
    preset_type: _common_pb2.PresetType
    symbol_id: int
    def __init__(self, preset_uuid: _Optional[str] = ..., preset_type: _Optional[_Union[_common_pb2.PresetType, str]] = ..., symbol_id: _Optional[int] = ...) -> None: ...

class PresetSymbolUpdateResponse(_message.Message):
    __slots__ = ("is_success",)
    IS_SUCCESS_FIELD_NUMBER: _ClassVar[int]
    is_success: bool
    def __init__(self, is_success: bool = ...) -> None: ...

class PresetSetFavoriteRequest(_message.Message):
    __slots__ = ("preset_uuid", "preset_type", "is_favorite")
    PRESET_UUID_FIELD_NUMBER: _ClassVar[int]
    PRESET_TYPE_FIELD_NUMBER: _ClassVar[int]
    IS_FAVORITE_FIELD_NUMBER: _ClassVar[int]
    preset_uuid: str
    preset_type: _common_pb2.PresetType
    is_favorite: bool
    def __init__(self, preset_uuid: _Optional[str] = ..., preset_type: _Optional[_Union[_common_pb2.PresetType, str]] = ..., is_favorite: bool = ...) -> None: ...

class PresetSetFavoriteResponse(_message.Message):
    __slots__ = ("is_success",)
    IS_SUCCESS_FIELD_NUMBER: _ClassVar[int]
    is_success: bool
    def __init__(self, is_success: bool = ...) -> None: ...

class CharacterPresetInfoRequest(_message.Message):
    __slots__ = ("preset_uuid",)
    PRESET_UUID_FIELD_NUMBER: _ClassVar[int]
    preset_uuid: str
    def __init__(self, preset_uuid: _Optional[str] = ...) -> None: ...

class CharacterPresetInfoResponse(_message.Message):
    __slots__ = ("is_success", "info")
    IS_SUCCESS_FIELD_NUMBER: _ClassVar[int]
    INFO_FIELD_NUMBER: _ClassVar[int]
    is_success: bool
    info: CharacterPresetInfo
    def __init__(self, is_success: bool = ..., info: _Optional[_Union[CharacterPresetInfo, _Mapping]] = ...) -> None: ...

class ForgettableSpellPresetInfoRequest(_message.Message):
    __slots__ = ("preset_uuid",)
    PRESET_UUID_FIELD_NUMBER: _ClassVar[int]
    preset_uuid: str
    def __init__(self, preset_uuid: _Optional[str] = ...) -> None: ...

class ForgettableSpellPresetInfoResponse(_message.Message):
    __slots__ = ("is_success", "info")
    IS_SUCCESS_FIELD_NUMBER: _ClassVar[int]
    INFO_FIELD_NUMBER: _ClassVar[int]
    is_success: bool
    info: ForgettableSpellPresetInfo
    def __init__(self, is_success: bool = ..., info: _Optional[_Union[ForgettableSpellPresetInfo, _Mapping]] = ...) -> None: ...

class PresetOutfitUpdateRequest(_message.Message):
    __slots__ = ("preset_uuid", "outfit_uuid")
    PRESET_UUID_FIELD_NUMBER: _ClassVar[int]
    OUTFIT_UUID_FIELD_NUMBER: _ClassVar[int]
    preset_uuid: str
    outfit_uuid: str
    def __init__(self, preset_uuid: _Optional[str] = ..., outfit_uuid: _Optional[str] = ...) -> None: ...

class PresetOutfitUpdateResponse(_message.Message):
    __slots__ = ("is_success", "updated_look")
    IS_SUCCESS_FIELD_NUMBER: _ClassVar[int]
    UPDATED_LOOK_FIELD_NUMBER: _ClassVar[int]
    is_success: bool
    updated_look: PresetLook
    def __init__(self, is_success: bool = ..., updated_look: _Optional[_Union[PresetLook, _Mapping]] = ...) -> None: ...

class PresetItemUpdateEvent(_message.Message):
    __slots__ = ("is_linked", "item_position_by_preset_uuid", "item_uid")
    class ItemPositionByPresetUuidEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: int
        def __init__(self, key: _Optional[str] = ..., value: _Optional[int] = ...) -> None: ...
    IS_LINKED_FIELD_NUMBER: _ClassVar[int]
    ITEM_POSITION_BY_PRESET_UUID_FIELD_NUMBER: _ClassVar[int]
    ITEM_UID_FIELD_NUMBER: _ClassVar[int]
    is_linked: bool
    item_position_by_preset_uuid: _containers.RepeatedCompositeFieldContainer[PresetItemUpdateEvent.ItemPositionByPresetUuidEntry]
    item_uid: int
    def __init__(self, is_linked: bool = ..., item_position_by_preset_uuid: _Optional[_Iterable[_Union[PresetItemUpdateEvent.ItemPositionByPresetUuidEntry, _Mapping]]] = ..., item_uid: _Optional[int] = ...) -> None: ...

class PresetListEvent(_message.Message):
    __slots__ = ("character_preset_info_by_id", "forgettable_spell_preset_info_by_id")
    class CharacterPresetInfoByIdEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: CharacterPresetInfo
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[CharacterPresetInfo, _Mapping]] = ...) -> None: ...
    class ForgettableSpellPresetInfoByIdEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: ForgettableSpellPresetInfo
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[ForgettableSpellPresetInfo, _Mapping]] = ...) -> None: ...
    CHARACTER_PRESET_INFO_BY_ID_FIELD_NUMBER: _ClassVar[int]
    FORGETTABLE_SPELL_PRESET_INFO_BY_ID_FIELD_NUMBER: _ClassVar[int]
    character_preset_info_by_id: _containers.RepeatedCompositeFieldContainer[PresetListEvent.CharacterPresetInfoByIdEntry]
    forgettable_spell_preset_info_by_id: _containers.RepeatedCompositeFieldContainer[PresetListEvent.ForgettableSpellPresetInfoByIdEntry]
    def __init__(self, character_preset_info_by_id: _Optional[_Iterable[_Union[PresetListEvent.CharacterPresetInfoByIdEntry, _Mapping]]] = ..., forgettable_spell_preset_info_by_id: _Optional[_Iterable[_Union[PresetListEvent.ForgettableSpellPresetInfoByIdEntry, _Mapping]]] = ...) -> None: ...

class CharacterPresetCurrentStateRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CharacterPresetCurrentStateResponse(_message.Message):
    __slots__ = ("preset",)
    PRESET_FIELD_NUMBER: _ClassVar[int]
    preset: CharacterPresetInfo
    def __init__(self, preset: _Optional[_Union[CharacterPresetInfo, _Mapping]] = ...) -> None: ...
