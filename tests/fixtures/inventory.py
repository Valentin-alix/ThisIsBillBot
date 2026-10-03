from DBDofusUnity.datas.protos.non_obf.game.common_pb2 import ObjectItem, ObjectItemInventory


def make_inventory_item(gid: int, quantity: int, uid: int = 0) -> ObjectItemInventory:
    return ObjectItemInventory(item=ObjectItem(uid=uid, gid=gid, quantity=quantity))
