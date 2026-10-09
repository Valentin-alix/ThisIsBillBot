from msgspec import Struct


class CellData(Struct, frozen=True):
    cellNumber: int
    speed: int
    mapChangeData: int
    moveZone: int
    linkedZone: int
    mov: int
    movDuringFight: bool
    movDuringRP: bool
    los: int
    farmCell: int
    visible: int
    havenbagCell: int
    floor: int
    red: int
    blue: int
    arrow: int

    def __hash__(self) -> int:
        return self.cellNumber.__hash__()


class Transform(Struct, frozen=True):
    m11: float
    m12: float
    m21: float
    m22: float
    m31: float
    m32: float


class MapPosition(Struct, frozen=True):
    x: float
    y: float


class MapReference(Struct, frozen=True):
    gfxId: int | None = None
    cellId: int | None = None
    transform: Transform | None = None
    m_interactionId: int | None = None
    innerCellRenderOrder: int | None = None
    position: MapPosition | None = None

    def __hash__(self) -> int:
        return (self.cellId, self.innerCellRenderOrder).__hash__()


class MapData(Struct, frozen=True):
    cellsData: list[CellData]


class MapDataRoot(Struct, frozen=True):
    references: list[MapReference]
    mapData: MapData
