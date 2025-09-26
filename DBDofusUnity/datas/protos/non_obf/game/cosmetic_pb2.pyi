import common_pb2 as _common_pb2
import appearance_pb2 as _appearance_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class UnknownOneHundredThirtyFour(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN_ONE_HUNDRED_THIRTY_FOUR: _ClassVar[UnknownOneHundredThirtyFour]

class UnknownOneHundredThirtyFive(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN_ONE_HUNDRED_THIRTY_FIVE: _ClassVar[UnknownOneHundredThirtyFive]

class UnknownOneHundredThirtySix(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN_ONE_HUNDRED_THIRTY_SIX: _ClassVar[UnknownOneHundredThirtySix]

class ObjectSlot(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    AMULET: _ClassVar[ObjectSlot]
    RING_LEFT: _ClassVar[ObjectSlot]
    RING_RIGHT: _ClassVar[ObjectSlot]
    BELT: _ClassVar[ObjectSlot]
    BOOTS: _ClassVar[ObjectSlot]
    PETMOUNT: _ClassVar[ObjectSlot]
    DRAGOTURKEY: _ClassVar[ObjectSlot]
    RHINEETLE: _ClassVar[ObjectSlot]
    SEEMYOOL: _ClassVar[ObjectSlot]
    CAPE: _ClassVar[ObjectSlot]
    HAT: _ClassVar[ObjectSlot]
    PET: _ClassVar[ObjectSlot]
    SHIELD: _ClassVar[ObjectSlot]
    BOW: _ClassVar[ObjectSlot]
    WAND: _ClassVar[ObjectSlot]
    STAFF: _ClassVar[ObjectSlot]
    DAGGER: _ClassVar[ObjectSlot]
    SCYTHE: _ClassVar[ObjectSlot]
    AXE: _ClassVar[ObjectSlot]
    LANCE: _ClassVar[ObjectSlot]
    HAMMER: _ClassVar[ObjectSlot]
    SHOVEL: _ClassVar[ObjectSlot]
    SWORD: _ClassVar[ObjectSlot]
    DISGUISE: _ClassVar[ObjectSlot]
    WINGS: _ClassVar[ObjectSlot]
    SHOULDERS: _ClassVar[ObjectSlot]
UNKNOWN_ONE_HUNDRED_THIRTY_FOUR: UnknownOneHundredThirtyFour
UNKNOWN_ONE_HUNDRED_THIRTY_FIVE: UnknownOneHundredThirtyFive
UNKNOWN_ONE_HUNDRED_THIRTY_SIX: UnknownOneHundredThirtySix
AMULET: ObjectSlot
RING_LEFT: ObjectSlot
RING_RIGHT: ObjectSlot
BELT: ObjectSlot
BOOTS: ObjectSlot
PETMOUNT: ObjectSlot
DRAGOTURKEY: ObjectSlot
RHINEETLE: ObjectSlot
SEEMYOOL: ObjectSlot
CAPE: ObjectSlot
HAT: ObjectSlot
PET: ObjectSlot
SHIELD: ObjectSlot
BOW: ObjectSlot
WAND: ObjectSlot
STAFF: ObjectSlot
DAGGER: ObjectSlot
SCYTHE: ObjectSlot
AXE: ObjectSlot
LANCE: ObjectSlot
HAMMER: ObjectSlot
SHOVEL: ObjectSlot
SWORD: ObjectSlot
DISGUISE: ObjectSlot
WINGS: ObjectSlot
SHOULDERS: ObjectSlot

class CosmeticInventoryLoadedEvent(_message.Message):
    __slots__ = ("objects",)
    OBJECTS_FIELD_NUMBER: _ClassVar[int]
    objects: _containers.RepeatedCompositeFieldContainer[_common_pb2.ObjectItem]
    def __init__(self, objects: _Optional[_Iterable[_Union[_common_pb2.ObjectItem, _Mapping]]] = ...) -> None: ...

class CosmeticInventoryAddObjectRequest(_message.Message):
    __slots__ = ("uid",)
    UID_FIELD_NUMBER: _ClassVar[int]
    uid: int
    def __init__(self, uid: _Optional[int] = ...) -> None: ...

class CosmeticInventoryAddObjectResponse(_message.Message):
    __slots__ = ("result",)
    class Result(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ERROR: _ClassVar[CosmeticInventoryAddObjectResponse.Result]
        DUPLICATE: _ClassVar[CosmeticInventoryAddObjectResponse.Result]
        SUCCESS: _ClassVar[CosmeticInventoryAddObjectResponse.Result]
    ERROR: CosmeticInventoryAddObjectResponse.Result
    DUPLICATE: CosmeticInventoryAddObjectResponse.Result
    SUCCESS: CosmeticInventoryAddObjectResponse.Result
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: CosmeticInventoryAddObjectResponse.Result
    def __init__(self, result: _Optional[_Union[CosmeticInventoryAddObjectResponse.Result, str]] = ...) -> None: ...

class CosmeticInventoryPopObjectRequest(_message.Message):
    __slots__ = ("gid",)
    GID_FIELD_NUMBER: _ClassVar[int]
    gid: int
    def __init__(self, gid: _Optional[int] = ...) -> None: ...

class CosmeticInventoryPopObjectResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class CosmeticInventoryLivingObjectFeedRequest(_message.Message):
    __slots__ = ("gid", "food_object_uid")
    GID_FIELD_NUMBER: _ClassVar[int]
    FOOD_OBJECT_UID_FIELD_NUMBER: _ClassVar[int]
    gid: int
    food_object_uid: int
    def __init__(self, gid: _Optional[int] = ..., food_object_uid: _Optional[int] = ...) -> None: ...

class CosmeticInventoryLivingObjectFeedResponse(_message.Message):
    __slots__ = ("success", "living_object_fed")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    LIVING_OBJECT_FED_FIELD_NUMBER: _ClassVar[int]
    success: bool
    living_object_fed: _common_pb2.ObjectItem
    def __init__(self, success: bool = ..., living_object_fed: _Optional[_Union[_common_pb2.ObjectItem, _Mapping]] = ...) -> None: ...

class CosmeticInventoryAddedEvent(_message.Message):
    __slots__ = ("object",)
    OBJECT_FIELD_NUMBER: _ClassVar[int]
    object: _common_pb2.ObjectItem
    def __init__(self, object: _Optional[_Union[_common_pb2.ObjectItem, _Mapping]] = ...) -> None: ...

class OutfitEquipAuraRequest(_message.Message):
    __slots__ = ("emote_id",)
    EMOTE_ID_FIELD_NUMBER: _ClassVar[int]
    emote_id: int
    def __init__(self, emote_id: _Optional[int] = ...) -> None: ...

class OutfitEquipAuraResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class OutfitAuraChangedEvent(_message.Message):
    __slots__ = ("emote_id",)
    EMOTE_ID_FIELD_NUMBER: _ClassVar[int]
    emote_id: int
    def __init__(self, emote_id: _Optional[int] = ...) -> None: ...

class OutfitEquipTitleRequest(_message.Message):
    __slots__ = ("title_id",)
    TITLE_ID_FIELD_NUMBER: _ClassVar[int]
    title_id: int
    def __init__(self, title_id: _Optional[int] = ...) -> None: ...

class OutfitEquipTitleResponse(_message.Message):
    __slots__ = ("success", "is_owned")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    IS_OWNED_FIELD_NUMBER: _ClassVar[int]
    success: bool
    is_owned: bool
    def __init__(self, success: bool = ..., is_owned: bool = ...) -> None: ...

class OutfitEquipOrnamentRequest(_message.Message):
    __slots__ = ("ornament_id",)
    ORNAMENT_ID_FIELD_NUMBER: _ClassVar[int]
    ornament_id: int
    def __init__(self, ornament_id: _Optional[int] = ...) -> None: ...

class OutfitEquipOrnamentResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class OutfitEquipObjectRequest(_message.Message):
    __slots__ = ("slot", "gid", "skin_id")
    SLOT_FIELD_NUMBER: _ClassVar[int]
    GID_FIELD_NUMBER: _ClassVar[int]
    SKIN_ID_FIELD_NUMBER: _ClassVar[int]
    slot: ObjectSlot
    gid: int
    skin_id: int
    def __init__(self, slot: _Optional[_Union[ObjectSlot, str]] = ..., gid: _Optional[int] = ..., skin_id: _Optional[int] = ...) -> None: ...

class OutfitEquipObjectResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class OutfitEquipObjectBestSlotRequest(_message.Message):
    __slots__ = ("gid", "skin_id")
    GID_FIELD_NUMBER: _ClassVar[int]
    SKIN_ID_FIELD_NUMBER: _ClassVar[int]
    gid: int
    skin_id: int
    def __init__(self, gid: _Optional[int] = ..., skin_id: _Optional[int] = ...) -> None: ...

class OutfitEquipObjectBestSlotResponse(_message.Message):
    __slots__ = ("success", "slot")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    SLOT_FIELD_NUMBER: _ClassVar[int]
    success: bool
    slot: ObjectSlot
    def __init__(self, success: bool = ..., slot: _Optional[_Union[ObjectSlot, str]] = ...) -> None: ...

class OutfitEquipFaceRequest(_message.Message):
    __slots__ = ("face_id",)
    FACE_ID_FIELD_NUMBER: _ClassVar[int]
    face_id: int
    def __init__(self, face_id: _Optional[int] = ...) -> None: ...

class OutfitEquipFaceResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class OutfitEquipColorsRequest(_message.Message):
    __slots__ = ("color_palette",)
    COLOR_PALETTE_FIELD_NUMBER: _ClassVar[int]
    color_palette: _appearance_pb2.ColorPalette
    def __init__(self, color_palette: _Optional[_Union[_appearance_pb2.ColorPalette, _Mapping]] = ...) -> None: ...

class OutfitEquipColorsResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class OutfitUpdateRequest(_message.Message):
    __slots__ = ("outfit_uuid", "name", "pictogram_id", "favorite")
    OUTFIT_UUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PICTOGRAM_ID_FIELD_NUMBER: _ClassVar[int]
    FAVORITE_FIELD_NUMBER: _ClassVar[int]
    outfit_uuid: str
    name: str
    pictogram_id: int
    favorite: bool
    def __init__(self, outfit_uuid: _Optional[str] = ..., name: _Optional[str] = ..., pictogram_id: _Optional[int] = ..., favorite: bool = ...) -> None: ...

class OutfitUpdateResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class OutfitCreateEmptyRequest(_message.Message):
    __slots__ = ("name", "pictogram_id", "face_id", "color_palette")
    NAME_FIELD_NUMBER: _ClassVar[int]
    PICTOGRAM_ID_FIELD_NUMBER: _ClassVar[int]
    FACE_ID_FIELD_NUMBER: _ClassVar[int]
    COLOR_PALETTE_FIELD_NUMBER: _ClassVar[int]
    name: str
    pictogram_id: int
    face_id: int
    color_palette: _appearance_pb2.ColorPalette
    def __init__(self, name: _Optional[str] = ..., pictogram_id: _Optional[int] = ..., face_id: _Optional[int] = ..., color_palette: _Optional[_Union[_appearance_pb2.ColorPalette, _Mapping]] = ...) -> None: ...

class OutfitDuplicateRequest(_message.Message):
    __slots__ = ("outfit_uuid", "name", "pictogram_id")
    OUTFIT_UUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PICTOGRAM_ID_FIELD_NUMBER: _ClassVar[int]
    outfit_uuid: str
    name: str
    pictogram_id: int
    def __init__(self, outfit_uuid: _Optional[str] = ..., name: _Optional[str] = ..., pictogram_id: _Optional[int] = ...) -> None: ...

class OutfitCreationResponse(_message.Message):
    __slots__ = ("success", "outfit_created")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    OUTFIT_CREATED_FIELD_NUMBER: _ClassVar[int]
    success: bool
    outfit_created: Outfit
    def __init__(self, success: bool = ..., outfit_created: _Optional[_Union[Outfit, _Mapping]] = ...) -> None: ...

class OutfitRemoveRequest(_message.Message):
    __slots__ = ("outfit_uuid",)
    OUTFIT_UUID_FIELD_NUMBER: _ClassVar[int]
    outfit_uuid: str
    def __init__(self, outfit_uuid: _Optional[str] = ...) -> None: ...

class OutfitRemoveResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class OutfitEquipRequest(_message.Message):
    __slots__ = ("outfit_uuid",)
    OUTFIT_UUID_FIELD_NUMBER: _ClassVar[int]
    outfit_uuid: str
    def __init__(self, outfit_uuid: _Optional[str] = ...) -> None: ...

class OutfitEquipResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class OutfitsLoadedEvent(_message.Message):
    __slots__ = ("current", "outfits")
    CURRENT_FIELD_NUMBER: _ClassVar[int]
    OUTFITS_FIELD_NUMBER: _ClassVar[int]
    current: Outfit
    outfits: _containers.RepeatedCompositeFieldContainer[Outfit]
    def __init__(self, current: _Optional[_Union[Outfit, _Mapping]] = ..., outfits: _Optional[_Iterable[_Union[Outfit, _Mapping]]] = ...) -> None: ...

class OutfitEntityLookChangedEvent(_message.Message):
    __slots__ = ("outfit_uuid", "entity_look")
    OUTFIT_UUID_FIELD_NUMBER: _ClassVar[int]
    ENTITY_LOOK_FIELD_NUMBER: _ClassVar[int]
    outfit_uuid: str
    entity_look: _common_pb2.EntityLook
    def __init__(self, outfit_uuid: _Optional[str] = ..., entity_look: _Optional[_Union[_common_pb2.EntityLook, _Mapping]] = ...) -> None: ...

class Outfit(_message.Message):
    __slots__ = ("uuid", "name", "pictogram_id", "objects", "aura_emote_id", "ornament_id", "title_id", "entity_look", "favorite", "last_modified", "face_id", "color_palette")
    class ObjectsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: Outfit.SkinOutfit
        def __init__(self, key: _Optional[int] = ..., value: _Optional[_Union[Outfit.SkinOutfit, _Mapping]] = ...) -> None: ...
    class SkinOutfit(_message.Message):
        __slots__ = ("gid", "skin")
        GID_FIELD_NUMBER: _ClassVar[int]
        SKIN_FIELD_NUMBER: _ClassVar[int]
        gid: int
        skin: int
        def __init__(self, gid: _Optional[int] = ..., skin: _Optional[int] = ...) -> None: ...
    UUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PICTOGRAM_ID_FIELD_NUMBER: _ClassVar[int]
    OBJECTS_FIELD_NUMBER: _ClassVar[int]
    AURA_EMOTE_ID_FIELD_NUMBER: _ClassVar[int]
    ORNAMENT_ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_ID_FIELD_NUMBER: _ClassVar[int]
    ENTITY_LOOK_FIELD_NUMBER: _ClassVar[int]
    FAVORITE_FIELD_NUMBER: _ClassVar[int]
    LAST_MODIFIED_FIELD_NUMBER: _ClassVar[int]
    FACE_ID_FIELD_NUMBER: _ClassVar[int]
    COLOR_PALETTE_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    name: str
    pictogram_id: int
    objects: _containers.MessageMap[int, Outfit.SkinOutfit]
    aura_emote_id: int
    ornament_id: int
    title_id: int
    entity_look: _common_pb2.EntityLook
    favorite: bool
    last_modified: str
    face_id: int
    color_palette: _appearance_pb2.ColorPalette
    def __init__(self, uuid: _Optional[str] = ..., name: _Optional[str] = ..., pictogram_id: _Optional[int] = ..., objects: _Optional[_Mapping[int, Outfit.SkinOutfit]] = ..., aura_emote_id: _Optional[int] = ..., ornament_id: _Optional[int] = ..., title_id: _Optional[int] = ..., entity_look: _Optional[_Union[_common_pb2.EntityLook, _Mapping]] = ..., favorite: bool = ..., last_modified: _Optional[str] = ..., face_id: _Optional[int] = ..., color_palette: _Optional[_Union[_appearance_pb2.ColorPalette, _Mapping]] = ...) -> None: ...

class UnknownOneHundredFortySix(_message.Message):
    __slots__ = ("unknown_three_hundred_eleven",)
    UNKNOWN_THREE_HUNDRED_ELEVEN_FIELD_NUMBER: _ClassVar[int]
    unknown_three_hundred_eleven: bool
    def __init__(self, unknown_three_hundred_eleven: bool = ...) -> None: ...

class UnknownOneHundredFortySeven(_message.Message):
    __slots__ = ("unknown_three_hundred_twelve",)
    UNKNOWN_THREE_HUNDRED_TWELVE_FIELD_NUMBER: _ClassVar[int]
    unknown_three_hundred_twelve: Outfit
    def __init__(self, unknown_three_hundred_twelve: _Optional[_Union[Outfit, _Mapping]] = ...) -> None: ...

class UnknownOneHundredFortyEight(_message.Message):
    __slots__ = ("unknown_three_hundred_thirteen",)
    UNKNOWN_THREE_HUNDRED_THIRTEEN_FIELD_NUMBER: _ClassVar[int]
    unknown_three_hundred_thirteen: UnknownOneHundredThirtyFour
    def __init__(self, unknown_three_hundred_thirteen: _Optional[_Union[UnknownOneHundredThirtyFour, str]] = ...) -> None: ...

class UnknownOneHundredFortyNine(_message.Message):
    __slots__ = ("unknown_three_hundred_fourteen",)
    UNKNOWN_THREE_HUNDRED_FOURTEEN_FIELD_NUMBER: _ClassVar[int]
    unknown_three_hundred_fourteen: bool
    def __init__(self, unknown_three_hundred_fourteen: bool = ...) -> None: ...

class OutfitEntityLookChangeRequest(_message.Message):
    __slots__ = ("slot", "hide")
    SLOT_FIELD_NUMBER: _ClassVar[int]
    HIDE_FIELD_NUMBER: _ClassVar[int]
    slot: ObjectSlot
    hide: bool
    def __init__(self, slot: _Optional[_Union[ObjectSlot, str]] = ..., hide: bool = ...) -> None: ...

class OutfitEntityLookChangeResponse(_message.Message):
    __slots__ = ("hide",)
    HIDE_FIELD_NUMBER: _ClassVar[int]
    hide: bool
    def __init__(self, hide: bool = ...) -> None: ...

class OutfitDetailResponse(_message.Message):
    __slots__ = ("success", "unknown_two_hundred_ninety", "outfit")
    class UnknownOneHundredThirtyTwo(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN_ONE_HUNDRED_THIRTY_TWO_UNSPECIFIED: _ClassVar[OutfitDetailResponse.UnknownOneHundredThirtyTwo]
    UNKNOWN_ONE_HUNDRED_THIRTY_TWO_UNSPECIFIED: OutfitDetailResponse.UnknownOneHundredThirtyTwo
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_TWO_HUNDRED_NINETY_FIELD_NUMBER: _ClassVar[int]
    OUTFIT_FIELD_NUMBER: _ClassVar[int]
    success: bool
    unknown_two_hundred_ninety: OutfitDetailResponse.UnknownOneHundredThirtyTwo
    outfit: Outfit
    def __init__(self, success: bool = ..., unknown_two_hundred_ninety: _Optional[_Union[OutfitDetailResponse.UnknownOneHundredThirtyTwo, str]] = ..., outfit: _Optional[_Union[Outfit, _Mapping]] = ...) -> None: ...

class OutfitSaveRequest(_message.Message):
    __slots__ = ("unknown_two_hundred_ninety_one", "name", "unknown_two_hundred_ninety_two")
    class UnknownOneHundredThirtyThree(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN_ONE_HUNDRED_THIRTY_THREE_UNSPECIFIED: _ClassVar[OutfitSaveRequest.UnknownOneHundredThirtyThree]
    UNKNOWN_ONE_HUNDRED_THIRTY_THREE_UNSPECIFIED: OutfitSaveRequest.UnknownOneHundredThirtyThree
    UNKNOWN_TWO_HUNDRED_NINETY_ONE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_TWO_HUNDRED_NINETY_TWO_FIELD_NUMBER: _ClassVar[int]
    unknown_two_hundred_ninety_one: int
    name: str
    unknown_two_hundred_ninety_two: OutfitSaveRequest.UnknownOneHundredThirtyThree
    def __init__(self, unknown_two_hundred_ninety_one: _Optional[int] = ..., name: _Optional[str] = ..., unknown_two_hundred_ninety_two: _Optional[_Union[OutfitSaveRequest.UnknownOneHundredThirtyThree, str]] = ...) -> None: ...

class UnknownOneHundredFifty(_message.Message):
    __slots__ = ("unknown_three_hundred_fifteen", "unknown_three_hundred_sixteen")
    class UnknownThreeHundredFifteenEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: UnknownOneHundredFifty.UnknownOneHundredFiftyOne
        def __init__(self, key: _Optional[int] = ..., value: _Optional[_Union[UnknownOneHundredFifty.UnknownOneHundredFiftyOne, _Mapping]] = ...) -> None: ...
    class UnknownOneHundredFiftyOne(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    UNKNOWN_THREE_HUNDRED_FIFTEEN_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_THREE_HUNDRED_SIXTEEN_FIELD_NUMBER: _ClassVar[int]
    unknown_three_hundred_fifteen: _containers.MessageMap[int, UnknownOneHundredFifty.UnknownOneHundredFiftyOne]
    unknown_three_hundred_sixteen: UnknownOneHundredThirtyFive
    def __init__(self, unknown_three_hundred_fifteen: _Optional[_Mapping[int, UnknownOneHundredFifty.UnknownOneHundredFiftyOne]] = ..., unknown_three_hundred_sixteen: _Optional[_Union[UnknownOneHundredThirtyFive, str]] = ...) -> None: ...

class UnknownOneHundredFiftyTwo(_message.Message):
    __slots__ = ("unknown_three_hundred_seventeen",)
    UNKNOWN_THREE_HUNDRED_SEVENTEEN_FIELD_NUMBER: _ClassVar[int]
    unknown_three_hundred_seventeen: bool
    def __init__(self, unknown_three_hundred_seventeen: bool = ...) -> None: ...

class UnknownOneHundredFiftyThree(_message.Message):
    __slots__ = ("unknown_three_hundred_eighteen",)
    class UnknownThreeHundredEighteenEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: UnknownOneHundredThirtySix
        def __init__(self, key: _Optional[int] = ..., value: _Optional[_Union[UnknownOneHundredThirtySix, str]] = ...) -> None: ...
    UNKNOWN_THREE_HUNDRED_EIGHTEEN_FIELD_NUMBER: _ClassVar[int]
    unknown_three_hundred_eighteen: _containers.ScalarMap[int, UnknownOneHundredThirtySix]
    def __init__(self, unknown_three_hundred_eighteen: _Optional[_Mapping[int, UnknownOneHundredThirtySix]] = ...) -> None: ...

class UnknownOneHundredFiftyFour(_message.Message):
    __slots__ = ("unknown_three_hundred_nineteen",)
    UNKNOWN_THREE_HUNDRED_NINETEEN_FIELD_NUMBER: _ClassVar[int]
    unknown_three_hundred_nineteen: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, unknown_three_hundred_nineteen: _Optional[_Iterable[int]] = ...) -> None: ...

class UnknownOneHundredFiftyFive(_message.Message):
    __slots__ = ("unknown_three_hundred_twenty", "unknown_three_hundred_twenty_one")
    UNKNOWN_THREE_HUNDRED_TWENTY_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_THREE_HUNDRED_TWENTY_ONE_FIELD_NUMBER: _ClassVar[int]
    unknown_three_hundred_twenty: str
    unknown_three_hundred_twenty_one: int
    def __init__(self, unknown_three_hundred_twenty: _Optional[str] = ..., unknown_three_hundred_twenty_one: _Optional[int] = ...) -> None: ...

class OutfitDetailRequest(_message.Message):
    __slots__ = ("outfit_uuid",)
    OUTFIT_UUID_FIELD_NUMBER: _ClassVar[int]
    outfit_uuid: str
    def __init__(self, outfit_uuid: _Optional[str] = ...) -> None: ...

class UnknownOneHundredFiftySix(_message.Message):
    __slots__ = ("unknown_three_hundred_twenty_two",)
    UNKNOWN_THREE_HUNDRED_TWENTY_TWO_FIELD_NUMBER: _ClassVar[int]
    unknown_three_hundred_twenty_two: bool
    def __init__(self, unknown_three_hundred_twenty_two: bool = ...) -> None: ...

class OutfitMenuRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
