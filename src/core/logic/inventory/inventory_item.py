from d3_mapping.resources.protos.game.common_pb2 import ObjectItemInventory
from models.datas.items_root import ItemsRootItem
from src.interfaces.enums.effect_action_enum import EffectActionEnum

INVENTORY_POSITION = 63


def is_weapon_hunter(object: ObjectItemInventory):
    return any(
        effect.action == EffectActionEnum.WEAPON_HUNTER
        for effect in object.item.effects
    )


def is_exchangeable_item(item: ItemsRootItem):
    return (item.m_flags & 8) != 0
