from msgspec import Struct


class CharacteristicsRootItem(Struct, frozen=True, kw_only=True):
    id: int
    keyword: str
    nameId: int
    asset: str
    categoryId: int
    visible: int
    order: int
    scaleFormulaId: int
    upgradable: int


CharacteristicsRoot = list[CharacteristicsRootItem]
