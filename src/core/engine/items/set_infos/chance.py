from DBDofusUnity.dofus_unity_reader.game_constants.characteristic import EffectElement
from DBDofusUnity.dofus_unity_reader.game_constants.inventory_position import (
    CharacterInventoryPositionEnum,
)
from DBDofusUnity.dofus_unity_reader.game_constants.item import ItemEnum

from src.core.engine.economy.sale_hotel import ItemToBuyInfo
from src.core.engine.items.set_infos.set_info import SetOnLevel

CHANCE_SETS: list[SetOnLevel] = [
    SetOnLevel(
        min_level=13,
        elem=EffectElement.CHANCE,
        item_info_by_position={
            CharacterInventoryPositionEnum.AccessoryPositionHat: ItemToBuyInfo(
                item_gid=ItemEnum.CHAPEAU_PIOU_BLEU, max_kamas=2_000
            ),
            CharacterInventoryPositionEnum.AccessoryPositionCape: ItemToBuyInfo(
                item_gid=ItemEnum.CAPE_PIOU_BLEU, max_kamas=2_000
            ),
            CharacterInventoryPositionEnum.AccessoryPositionAmulet: ItemToBuyInfo(
                item_gid=ItemEnum.AMU_PIOU_BLEU, max_kamas=2_000
            ),
            CharacterInventoryPositionEnum.InventoryPositionRingLeft: ItemToBuyInfo(
                item_gid=ItemEnum.ANNEAU_PIOU_BLEU, max_kamas=2_000
            ),
            CharacterInventoryPositionEnum.InventoryPositionRingRight: ItemToBuyInfo(
                item_gid=ItemEnum.ANNEAU_KARDORIM, max_kamas=2_000
            ),
            CharacterInventoryPositionEnum.AccessoryPositionBelt: ItemToBuyInfo(
                item_gid=ItemEnum.CEINTURE_PIOU_BLEU, max_kamas=2_000
            ),
            CharacterInventoryPositionEnum.AccessoryPositionBoots: ItemToBuyInfo(
                item_gid=ItemEnum.SANDALE_PIOU_BLEU, max_kamas=2_000
            ),
            CharacterInventoryPositionEnum.AccessoryPositionWeapon: ItemToBuyInfo(
                item_gid=ItemEnum.ARC_HOLLIS, max_kamas=2_000
            ),
        },
    ),
    SetOnLevel(
        elem=EffectElement.CHANCE,
        min_level=43,
        item_info_by_position={
            CharacterInventoryPositionEnum.AccessoryPositionHat: ItemToBuyInfo(
                item_gid=ItemEnum.CHAPEAU_AKWADALA, max_kamas=60_000
            ),
            CharacterInventoryPositionEnum.AccessoryPositionCape: ItemToBuyInfo(
                item_gid=ItemEnum.CAPE_AKWADALA, max_kamas=60_000
            ),
            CharacterInventoryPositionEnum.AccessoryPositionAmulet: ItemToBuyInfo(
                item_gid=ItemEnum.AMULETTE_AKWADALA, max_kamas=60_000
            ),
            CharacterInventoryPositionEnum.InventoryPositionRingLeft: ItemToBuyInfo(
                item_gid=ItemEnum.ANNEAU_PIOU_BLEU, max_kamas=2_000
            ),
            CharacterInventoryPositionEnum.InventoryPositionRingRight: ItemToBuyInfo(
                item_gid=ItemEnum.ALLIANCE_AKWADALA, max_kamas=60_000
            ),
            CharacterInventoryPositionEnum.AccessoryPositionBelt: ItemToBuyInfo(
                item_gid=ItemEnum.CEINTURE_AKWADALA, max_kamas=60_000
            ),
            CharacterInventoryPositionEnum.AccessoryPositionBoots: ItemToBuyInfo(
                item_gid=ItemEnum.GETA_AKWADALA, max_kamas=60_000
            ),
            CharacterInventoryPositionEnum.AccessoryPositionWeapon: ItemToBuyInfo(
                item_gid=ItemEnum.BATON_AKWADALA, max_kamas=60_000
            ),
            CharacterInventoryPositionEnum.InventoryPositionDofus1: ItemToBuyInfo(
                item_gid=ItemEnum.DOFUS_ARGENTE, max_kamas=60_000
            ),
        },
    ),
    SetOnLevel(
        elem=EffectElement.CHANCE,
        min_level=80,
        item_info_by_position={
            CharacterInventoryPositionEnum.AccessoryPositionHat: ItemToBuyInfo(
                item_gid=ItemEnum.CARACOIFFE, max_kamas=100_000
            ),
            CharacterInventoryPositionEnum.AccessoryPositionCape: ItemToBuyInfo(
                item_gid=ItemEnum.CARACAPE, max_kamas=100_000
            ),
            CharacterInventoryPositionEnum.AccessoryPositionAmulet: ItemToBuyInfo(
                item_gid=ItemEnum.AMUBLOP_GRIOTTE_ROYALE, max_kamas=100_000
            ),
            CharacterInventoryPositionEnum.InventoryPositionRingLeft: ItemToBuyInfo(
                item_gid=ItemEnum.BLOPANNEAU_GRIOTTE_ROYAL, max_kamas=100_000
            ),
            CharacterInventoryPositionEnum.InventoryPositionRingRight: ItemToBuyInfo(
                item_gid=ItemEnum.GELANO, max_kamas=100_000
            ),
            CharacterInventoryPositionEnum.AccessoryPositionBelt: ItemToBuyInfo(
                item_gid=ItemEnum.BLOPTURE_GRIOTTE_ROYALE, max_kamas=100_000
            ),
            CharacterInventoryPositionEnum.AccessoryPositionBoots: ItemToBuyInfo(
                item_gid=ItemEnum.BLOPTES_GRIOTTE_ROYALES, max_kamas=100_000
            ),
            CharacterInventoryPositionEnum.AccessoryPositionWeapon: ItemToBuyInfo(
                item_gid=ItemEnum.ARES, max_kamas=100_000
            ),
            CharacterInventoryPositionEnum.AccessoryPositionShield: ItemToBuyInfo(
                item_gid=ItemEnum.BOUCLIER_CHEF_CROCODAILLE, max_kamas=100_000
            ),
            CharacterInventoryPositionEnum.InventoryPositionDofus1: ItemToBuyInfo(
                item_gid=ItemEnum.DOFUS_CAWOTTE, max_kamas=100_000
            ),
            CharacterInventoryPositionEnum.InventoryPositionDofus2: ItemToBuyInfo(
                item_gid=ItemEnum.DOFUS_ARGENTE, max_kamas=100_000
            ),
            CharacterInventoryPositionEnum.InventoryPositionDofus3: ItemToBuyInfo(
                item_gid=ItemEnum.DOKOKO, max_kamas=100_000
            ),
            CharacterInventoryPositionEnum.InventoryPositionDofus4: ItemToBuyInfo(
                item_gid=ItemEnum.CUIRASSE_NEUTRE_MINEUR, max_kamas=100_000
            ),
            CharacterInventoryPositionEnum.InventoryPositionDofus5: ItemToBuyInfo(
                item_gid=ItemEnum.MURAILLE_NEUTRE_MINEURE, max_kamas=100_000
            ),
        },
    ),
]
