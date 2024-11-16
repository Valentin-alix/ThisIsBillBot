from enum import IntEnum

from D3Database.models.datas.items_root import ItemsRootItem
from D3Mapping.d3_mapping.resources.protos.game.common_pb2 import ObjectItemInventory
from src.core.engine.fights.effect import EffectActionEnum


def is_weapon_hunter(object: ObjectItemInventory):
    return any(
        effect.action == EffectActionEnum.WEAPON_HUNTER
        for effect in object.item.effects
    )


def is_exchangeable_item(item: ItemsRootItem):
    return (item.m_flags & 8) != 0


class SetPositionEnum(IntEnum):
    COIFFE = 6
    CAPE = 7
    ARME = 1
    BOUCLIER = 15
    AMU = 0
    ANNEAU_1 = 2
    ANNEAU_2 = 4
    CEINTURE = 3
    BOTTES = 5
