from d3_mapping.resources.protos.game.common_pb2 import ObjectItemInventory


def get_weight_item_for_sale_hotel(
    item_gid: int,
    avg_price_by_gid: dict[int, float],
    storage_object_by_item: dict[int, ObjectItemInventory] | None,
):
    if storage_object_by_item is not None:
        return avg_price_by_gid.get(item_gid, 1) * (
            related_object.item.quantity
            if (related_object := storage_object_by_item.get(item_gid))
            else 0
        )
    return avg_price_by_gid.get(item_gid, 1)
