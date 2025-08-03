from msgspec import Struct


class CharacteristicCategoriesRootItem(Struct, frozen=True, kw_only=True):
    id: int
    nameId: int
    order: int
    characteristicIds: list[int]


CharacteristicCategoriesRoot = list[CharacteristicCategoriesRootItem]
