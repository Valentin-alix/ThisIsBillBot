from enum import IntEnum, auto

from src.core.config import BOT_KAMA_LIMIT_TO_GIVE
from src.core.engine.movements.map.map_tools import MapTools
from src.core.engine.npcs.npc_info import NpcInfo
from src.core.game_constants import NPCs


class CharacterInventoryPositionEnum(IntEnum):
    AccessoryPositionHat = 6

    AccessoryPositionCape = 7

    AccessoryPositionBelt = 3

    AccessoryPositionBoots = 5

    AccessoryPositionAmulet = 0

    AccessoryPositionShield = 15

    AccessoryPositionWeapon = 1

    AccessoryPositionPets = 8

    AccessoryPositionRideHarness = 29

    InventoryPositionRingLeft = 2

    InventoryPositionRingRight = 4

    InventoryPositionDofus1 = 9

    InventoryPositionDofus2 = 10

    InventoryPositionDofus3 = 11

    InventoryPositionDofus4 = 12

    InventoryPositionDofus5 = 13

    InventoryPositionDofus6 = 14

    InventoryPositionMount = 16

    InventoryPositionMutation = 20

    InventoryPositionBoostFood = 21

    InventoryPositionFirstBonus = 22

    InventoryPositionSecondBonus = 23

    InventoryPositionFirstMalus = 24

    InventoryPositionSecondMalus = 25

    InventoryPositionRoleplayBuffer = 26

    InventoryPositionFollower = 27

    InventoryPositionEntity = 28

    InventoryPositionCostume = 30

    InventoryPositionConsumable = 31
    InventoryPositionDofus7 = 32
    InventoryPositionDofus8 = 33
    InventoryPositionDofus9 = 34
    InventoryPositionDofus10 = 35
    InventoryPositionDofus11 = 36
    InventoryPositionDofus12 = 37
    InventoryPositionPlastron = 38
    InventoryPositionEmbleme = 39
    InventoryPositionTalisman = 40

    InventoryPositionNotEquiped = 63


class ActionEnum(IntEnum):
    LINKED_TO_CHARACTER = auto()


def do_unload_on_mule(
    kamas: int,
    is_sub: bool,
    is_full_object_in_sale_hotel: bool,
    should_update_price: bool,
) -> bool:
    return kamas > BOT_KAMA_LIMIT_TO_GIVE or (
        not is_sub and is_full_object_in_sale_hotel and not should_update_price
    )


def get_bank_npc_info(is_sub: bool) -> list[NpcInfo]:
    return [
        npc_info
        for npc_info in NPCs.BANKS
        if is_sub or MapTools.is_map_allowed_for_unsub(npc_info.npc_map_id)
    ]
