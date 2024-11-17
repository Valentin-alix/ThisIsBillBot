from D3Database.data_center.data_reader import DataReader
from D3Database.data_center.i18n import I18N
from D3Mapping.d3_mapping.resources.protos.game.common_pb2 import ObjectItemInventory


def format_item_name(gid: int) -> str:
    item = DataReader().item_by_id[gid]
    return I18N().name_by_id[item.nameId]


def format_item_with_quantity(obj: ObjectItemInventory) -> str:
    name = format_item_name(obj.item.gid)
    return f"{name} x{obj.item.quantity}"


def format_items_list(objects: list[ObjectItemInventory]) -> str:
    if not objects:
        return "[]"
    items_str = ", ".join(format_item_with_quantity(obj) for obj in objects[:5])
    if len(objects) > 5:
        items_str += f" ... (+{len(objects) - 5} more)"
    return f"[{items_str}]"


def format_items_count_by_name(objects: list[ObjectItemInventory]) -> str:
    if not objects:
        return "0 items"
    unique_gids = {obj.item.gid for obj in objects}
    return f"{len(objects)} items ({len(unique_gids)} unique)"
