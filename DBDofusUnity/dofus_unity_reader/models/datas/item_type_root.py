from msgspec import Struct


class ItemTypeData(Struct, frozen=True, kw_only=True):
    id: int
    nameId: int
    superTypeId: int
    categoryId: int
    isInEncyclopedia: int
    craftXpRatio: int
    evolutiveTypeId: int
    rawZone: str


ItemsTypeRoot = list[ItemTypeData]
