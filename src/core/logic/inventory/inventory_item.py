from d3_mapping.resources.protos.game.common_pb2 import ObjectItemInventory
from src.interfaces.enums.effect_action_enum import EffectActionEnum


def is_weapon_hunter(object: ObjectItemInventory):
    return any(
        effect.action == EffectActionEnum.WEAPON_HUNTER
        for effect in object.item.effects
    )
