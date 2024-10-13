from protos.game.common_pb2 import ObjectItemInventory
from src.core.data_center.data_reader import DataReader


def get_weight_item_for_sale_hotel(
    item_gid: int,
    avg_price_by_gid: dict[int, float],
    gatherer_object_tab: dict[int, ObjectItemInventory] | None,
):
    if gatherer_object_tab is not None:
        return (
            avg_price_by_gid.get(item_gid, 1)
            * (
                related_object.item.quantity
                if (related_object := gatherer_object_tab.get(item_gid))
                else 0
            )
            / (1.5 if DataReader().item_by_id[item_gid].level == 200 else 1)
        )
    return avg_price_by_gid.get(item_gid, 1)
