from typing import Any

import msgspec

from DBDofusUnity.dofus_unity_reader.models.maps import (
    CellData,
    MapData,
    MapDataRoot,
    MapPosition,
    MapReference,
)


class ClientCellData(msgspec.Struct, frozen=True, kw_only=True):
    cellNumber: int
    speed: int
    mapChangeData: int
    moveZone: int
    linkedZone: int
    mov: int
    los: int
    farmCell: int
    visible: int
    havenbagCell: int
    floor: int = msgspec.field(name="altitude")
    red: int
    blue: int
    arrow: int


class MapCellDataExport(ClientCellData, frozen=True, kw_only=True):
    floor: int = msgspec.field(name="floor")
    nonWalkableDuringFight: int
    nonWalkableDuringRP: int


class MapDataExport(msgspec.Struct, frozen=True):
    cellsData: list[MapCellDataExport]


class MapExport(msgspec.Struct, frozen=True):
    references: list[MapReference]
    mapData: MapDataExport


def _normalize_cell(cell: ClientCellData) -> CellData:
    mov_during_fight = mov_during_rp = bool(cell.mov)
    if isinstance(cell, MapCellDataExport):
        mov_during_fight = mov_during_fight and not cell.nonWalkableDuringFight
        mov_during_rp = mov_during_rp and not cell.nonWalkableDuringRP
    return msgspec.convert(
        {
            **msgspec.structs.asdict(cell),
            "movDuringFight": mov_during_fight,
            "movDuringRP": mov_during_rp,
        },
        type=CellData,
    )


class ElementReference(msgspec.Struct, frozen=True):
    rid: int


class PlacedMapElements(msgspec.Struct, frozen=True):
    mapElements: list[ElementReference]
    cellId: int
    displayOrder: int


class LayerMapElements(msgspec.Struct, frozen=True):
    mapElements: list[ElementReference]


class ClientMapReference(msgspec.Struct, frozen=True, kw_only=True):
    rid: int
    gfxId: int | None = None
    cellId: int | None = None
    displayOrder: int | None = None
    position: MapPosition | None = None
    interactiveId: int | None = msgspec.field(default=None, name="<interactiveId>k__BackingField")


class ClientMapData(msgspec.Struct, frozen=True):
    cellsData: list[ClientCellData]
    references: list[ClientMapReference]
    middlegroundMapElements: list[PlacedMapElements]
    backgroundMapElements: list[LayerMapElements]
    foregroundMapElements: list[LayerMapElements]


def decode_map_export(raw: bytes) -> MapDataRoot:
    root = msgspec.json.decode(raw, type=dict[str, Any])
    if "cellsData" in root:
        data = msgspec.convert(root, type=ClientMapData)
        placements = {
            element.rid: (group.cellId, group.displayOrder)
            for group in data.middlegroundMapElements
            for element in group.mapElements
        }
        unplaced_layer_rids = {
            element.rid
            for group in data.backgroundMapElements + data.foregroundMapElements
            for element in group.mapElements
        }
        references: list[MapReference] = []
        for ref in data.references:
            cell_id, order = placements.get(ref.rid, (ref.cellId, ref.displayOrder))
            if ref.interactiveId is not None and cell_id is None and ref.rid not in unplaced_layer_rids:
                raise ValueError(f"Interactive {ref.interactiveId} has no cell placement")
            references.append(
                MapReference(
                    gfxId=ref.gfxId,
                    cellId=cell_id,
                    m_interactionId=ref.interactiveId,
                    innerCellRenderOrder=order,
                    position=ref.position,
                )
            )
        result = MapDataRoot(
            references=references,
            mapData=MapData(
                cellsData=[_normalize_cell(cell) for cell in data.cellsData]
            ),
        )
    else:
        exported = msgspec.convert(root, type=MapExport)
        result = MapDataRoot(
            references=exported.references,
            mapData=MapData(cellsData=[_normalize_cell(cell) for cell in exported.mapData.cellsData]),
        )
    if [cell.cellNumber for cell in result.mapData.cellsData] != list(range(560)):
        raise ValueError("Map export must contain the 560 cells in cell number order")
    return result
