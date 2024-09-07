from com.ankama.dofus.server.game.protocol import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class HouseInformationRequest(_message.Message):
    __slots__ = ("house_id", "house_instance_id")
    HOUSE_ID_FIELD_NUMBER: _ClassVar[int]
    HOUSE_INSTANCE_ID_FIELD_NUMBER: _ClassVar[int]
    house_id: int
    house_instance_id: int
    def __init__(self, house_id: _Optional[int] = ..., house_instance_id: _Optional[int] = ...) -> None: ...

class HouseInformationResponse(_message.Message):
    __slots__ = ("house_information",)
    HOUSE_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    house_information: _common_pb2.HouseInstance
    def __init__(self, house_information: _Optional[_Union[_common_pb2.HouseInstance, _Mapping]] = ...) -> None: ...

class HouseKickRequest(_message.Message):
    __slots__ = ("player_id",)
    PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
    player_id: int
    def __init__(self, player_id: _Optional[int] = ...) -> None: ...

class HouseSellRequest(_message.Message):
    __slots__ = ("instance_id", "amount", "for_sale", "is_inside")
    INSTANCE_ID_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    FOR_SALE_FIELD_NUMBER: _ClassVar[int]
    IS_INSIDE_FIELD_NUMBER: _ClassVar[int]
    instance_id: int
    amount: int
    for_sale: bool
    is_inside: bool
    def __init__(self, instance_id: _Optional[int] = ..., amount: _Optional[int] = ..., for_sale: bool = ..., is_inside: bool = ...) -> None: ...

class HouseBuyRequest(_message.Message):
    __slots__ = ("proposed_price",)
    PROPOSED_PRICE_FIELD_NUMBER: _ClassVar[int]
    proposed_price: int
    def __init__(self, proposed_price: _Optional[int] = ...) -> None: ...

class HouseLockFromInsideRequest(_message.Message):
    __slots__ = ("code",)
    CODE_FIELD_NUMBER: _ClassVar[int]
    code: str
    def __init__(self, code: _Optional[str] = ...) -> None: ...

class HousesToSellRequest(_message.Message):
    __slots__ = ("page_index",)
    PAGE_INDEX_FIELD_NUMBER: _ClassVar[int]
    page_index: int
    def __init__(self, page_index: _Optional[int] = ...) -> None: ...

class HousesToSellFiltersRequest(_message.Message):
    __slots__ = ("area_id", "at_least_room_number", "at_least_chest_number", "skill_requested", "price_max", "order_by")
    AREA_ID_FIELD_NUMBER: _ClassVar[int]
    AT_LEAST_ROOM_NUMBER_FIELD_NUMBER: _ClassVar[int]
    AT_LEAST_CHEST_NUMBER_FIELD_NUMBER: _ClassVar[int]
    SKILL_REQUESTED_FIELD_NUMBER: _ClassVar[int]
    PRICE_MAX_FIELD_NUMBER: _ClassVar[int]
    ORDER_BY_FIELD_NUMBER: _ClassVar[int]
    area_id: int
    at_least_room_number: int
    at_least_chest_number: int
    skill_requested: int
    price_max: int
    order_by: _common_pb2.RealEstateOrder
    def __init__(self, area_id: _Optional[int] = ..., at_least_room_number: _Optional[int] = ..., at_least_chest_number: _Optional[int] = ..., skill_requested: _Optional[int] = ..., price_max: _Optional[int] = ..., order_by: _Optional[_Union[_common_pb2.RealEstateOrder, str]] = ...) -> None: ...

class HouseTeleportRequest(_message.Message):
    __slots__ = ("house_id", "instance_id")
    HOUSE_ID_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_ID_FIELD_NUMBER: _ClassVar[int]
    house_id: int
    instance_id: int
    def __init__(self, house_id: _Optional[int] = ..., instance_id: _Optional[int] = ...) -> None: ...

class HouseGuildRightsViewRequest(_message.Message):
    __slots__ = ("house_id", "instance_id")
    HOUSE_ID_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_ID_FIELD_NUMBER: _ClassVar[int]
    house_id: int
    instance_id: int
    def __init__(self, house_id: _Optional[int] = ..., instance_id: _Optional[int] = ...) -> None: ...

class HouseGuildShareRequest(_message.Message):
    __slots__ = ("house_id", "instance_id", "share", "rights")
    HOUSE_ID_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_ID_FIELD_NUMBER: _ClassVar[int]
    SHARE_FIELD_NUMBER: _ClassVar[int]
    RIGHTS_FIELD_NUMBER: _ClassVar[int]
    house_id: int
    instance_id: int
    share: bool
    rights: int
    def __init__(self, house_id: _Optional[int] = ..., instance_id: _Optional[int] = ..., share: bool = ..., rights: _Optional[int] = ...) -> None: ...

class HouseAccountEvent(_message.Message):
    __slots__ = ("houses",)
    HOUSES_FIELD_NUMBER: _ClassVar[int]
    houses: _containers.RepeatedCompositeFieldContainer[_common_pb2.House]
    def __init__(self, houses: _Optional[_Iterable[_Union[_common_pb2.House, _Mapping]]] = ...) -> None: ...

class HousePropertiesEvent(_message.Message):
    __slots__ = ("house_id", "doors_on_map", "properties")
    HOUSE_ID_FIELD_NUMBER: _ClassVar[int]
    DOORS_ON_MAP_FIELD_NUMBER: _ClassVar[int]
    PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    house_id: int
    doors_on_map: _containers.RepeatedScalarFieldContainer[int]
    properties: _common_pb2.HouseInstance
    def __init__(self, house_id: _Optional[int] = ..., doors_on_map: _Optional[_Iterable[int]] = ..., properties: _Optional[_Union[_common_pb2.HouseInstance, _Mapping]] = ...) -> None: ...

class HouseBuyResultEvent(_message.Message):
    __slots__ = ("house_id", "instance_id", "second_hand", "bought", "price")
    HOUSE_ID_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_ID_FIELD_NUMBER: _ClassVar[int]
    SECOND_HAND_FIELD_NUMBER: _ClassVar[int]
    BOUGHT_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    house_id: int
    instance_id: int
    second_hand: bool
    bought: bool
    price: int
    def __init__(self, house_id: _Optional[int] = ..., instance_id: _Optional[int] = ..., second_hand: bool = ..., bought: bool = ..., price: _Optional[int] = ...) -> None: ...

class HouseSellingUpdateEvent(_message.Message):
    __slots__ = ("house_id", "instance_id", "second_hand", "price", "buyer_account_nickname", "buyer_account_tag")
    HOUSE_ID_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_ID_FIELD_NUMBER: _ClassVar[int]
    SECOND_HAND_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    BUYER_ACCOUNT_NICKNAME_FIELD_NUMBER: _ClassVar[int]
    BUYER_ACCOUNT_TAG_FIELD_NUMBER: _ClassVar[int]
    house_id: int
    instance_id: int
    second_hand: bool
    price: int
    buyer_account_nickname: str
    buyer_account_tag: str
    def __init__(self, house_id: _Optional[int] = ..., instance_id: _Optional[int] = ..., second_hand: bool = ..., price: _Optional[int] = ..., buyer_account_nickname: _Optional[str] = ..., buyer_account_tag: _Optional[str] = ...) -> None: ...

class HousesToSellEvent(_message.Message):
    __slots__ = ("page_index", "total_page", "houses")
    class HouseToSell(_message.Message):
        __slots__ = ("instance_id", "second_hand", "model_id", "owner_account_nickname", "owner_account_tag", "has_owner", "owner_name", "coordinates", "sub_area_id", "room_number", "chest_number", "skills_id", "is_locked", "price")
        INSTANCE_ID_FIELD_NUMBER: _ClassVar[int]
        SECOND_HAND_FIELD_NUMBER: _ClassVar[int]
        MODEL_ID_FIELD_NUMBER: _ClassVar[int]
        OWNER_ACCOUNT_NICKNAME_FIELD_NUMBER: _ClassVar[int]
        OWNER_ACCOUNT_TAG_FIELD_NUMBER: _ClassVar[int]
        HAS_OWNER_FIELD_NUMBER: _ClassVar[int]
        OWNER_NAME_FIELD_NUMBER: _ClassVar[int]
        COORDINATES_FIELD_NUMBER: _ClassVar[int]
        SUB_AREA_ID_FIELD_NUMBER: _ClassVar[int]
        ROOM_NUMBER_FIELD_NUMBER: _ClassVar[int]
        CHEST_NUMBER_FIELD_NUMBER: _ClassVar[int]
        SKILLS_ID_FIELD_NUMBER: _ClassVar[int]
        IS_LOCKED_FIELD_NUMBER: _ClassVar[int]
        PRICE_FIELD_NUMBER: _ClassVar[int]
        instance_id: int
        second_hand: bool
        model_id: int
        owner_account_nickname: str
        owner_account_tag: str
        has_owner: bool
        owner_name: str
        coordinates: _common_pb2.MapCoordinates
        sub_area_id: int
        room_number: int
        chest_number: int
        skills_id: _containers.RepeatedScalarFieldContainer[int]
        is_locked: bool
        price: int
        def __init__(self, instance_id: _Optional[int] = ..., second_hand: bool = ..., model_id: _Optional[int] = ..., owner_account_nickname: _Optional[str] = ..., owner_account_tag: _Optional[str] = ..., has_owner: bool = ..., owner_name: _Optional[str] = ..., coordinates: _Optional[_Union[_common_pb2.MapCoordinates, _Mapping]] = ..., sub_area_id: _Optional[int] = ..., room_number: _Optional[int] = ..., chest_number: _Optional[int] = ..., skills_id: _Optional[_Iterable[int]] = ..., is_locked: bool = ..., price: _Optional[int] = ...) -> None: ...
    PAGE_INDEX_FIELD_NUMBER: _ClassVar[int]
    TOTAL_PAGE_FIELD_NUMBER: _ClassVar[int]
    HOUSES_FIELD_NUMBER: _ClassVar[int]
    page_index: int
    total_page: int
    houses: _containers.RepeatedCompositeFieldContainer[HousesToSellEvent.HouseToSell]
    def __init__(self, page_index: _Optional[int] = ..., total_page: _Optional[int] = ..., houses: _Optional[_Iterable[_Union[HousesToSellEvent.HouseToSell, _Mapping]]] = ...) -> None: ...

class HouseGuildNoneEvent(_message.Message):
    __slots__ = ("house_id", "instance_id", "second_hand")
    HOUSE_ID_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_ID_FIELD_NUMBER: _ClassVar[int]
    SECOND_HAND_FIELD_NUMBER: _ClassVar[int]
    house_id: int
    instance_id: int
    second_hand: bool
    def __init__(self, house_id: _Optional[int] = ..., instance_id: _Optional[int] = ..., second_hand: bool = ...) -> None: ...

class HouseGuildRightsEvent(_message.Message):
    __slots__ = ("house_id", "instance_id", "second_hand", "guild_information", "rights", "is_locked")
    HOUSE_ID_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_ID_FIELD_NUMBER: _ClassVar[int]
    SECOND_HAND_FIELD_NUMBER: _ClassVar[int]
    GUILD_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    RIGHTS_FIELD_NUMBER: _ClassVar[int]
    IS_LOCKED_FIELD_NUMBER: _ClassVar[int]
    house_id: int
    instance_id: int
    second_hand: bool
    guild_information: _common_pb2.GuildInformation
    rights: int
    is_locked: bool
    def __init__(self, house_id: _Optional[int] = ..., instance_id: _Optional[int] = ..., second_hand: bool = ..., guild_information: _Optional[_Union[_common_pb2.GuildInformation, _Mapping]] = ..., rights: _Optional[int] = ..., is_locked: bool = ...) -> None: ...
