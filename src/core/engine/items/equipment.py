from collections import Counter
from collections.abc import Iterable

from DBDofusUnity.datas.protos.non_obf.game.common_pb2 import ObjectItemInventory
from DBDofusUnity.dofus_unity_reader.data_center.data_reader import DataReader
from DBDofusUnity.dofus_unity_reader.game_constants.characteristic import (
    CharacteristicEnum,
    EffectElement,
)
from DBDofusUnity.dofus_unity_reader.game_constants.inventory_position import (
    CharacterInventoryPositionEnum,
)

from src.core.engine.economy.sale_hotel import ItemToBuyInfo
from src.core.engine.fights.damage_calculator import ELEMENT_INFO_BY_ID
from src.core.engine.items import set_infos
from src.core.engine.items.item import get_equipment_on_position

_BASE_ROLL_WEIGHT: dict[int, float] = {
    CharacteristicEnum.ACTION_POINTS: 50.0,
    CharacteristicEnum.MOVEMENT_POINTS: 20.0,
    CharacteristicEnum.RANGE: 6.0,
    CharacteristicEnum.POWER: 4.0,
    CharacteristicEnum.ALL_DAMAGES_BONUS: 4.0,
    CharacteristicEnum.DAMAGES_FACTOR: 4.0,
    CharacteristicEnum.DAMAGES_PERCENT_SPELL: 4.0,
    CharacteristicEnum.CRITICAL_DAMAGE_BONUS: 3.5,
    CharacteristicEnum.CRITICAL_HIT: 3.0,
    CharacteristicEnum.WISDOM: 1.5,
    CharacteristicEnum.VITALITY: 1.0,
}
_PRIMARY_FLAT_DAMAGE_WEIGHT = 6.0
_PRIMARY_SCALING_WEIGHT = 3.0
_DEFAULT_ROLL_WEIGHT = 0.5

_WEAPON_TYPE_IDS = frozenset({2, 3, 4, 5, 6, 7, 8, 19, 20, 21, 22, 81, 89})
_EQUIPMENT_POSITIONS_BY_TYPE_ID: dict[int, tuple[CharacterInventoryPositionEnum, ...]] = {
    1: (CharacterInventoryPositionEnum.AccessoryPositionAmulet,),
    9: (
        CharacterInventoryPositionEnum.InventoryPositionRingLeft,
        CharacterInventoryPositionEnum.InventoryPositionRingRight,
    ),
    10: (CharacterInventoryPositionEnum.AccessoryPositionBelt,),
    11: (CharacterInventoryPositionEnum.AccessoryPositionBoots,),
    15: (CharacterInventoryPositionEnum.AccessoryPositionShield,),
    16: (CharacterInventoryPositionEnum.AccessoryPositionHat,),
    17: (CharacterInventoryPositionEnum.AccessoryPositionCape,),
    18: (CharacterInventoryPositionEnum.AccessoryPositionPets,),
    23: tuple(
        CharacterInventoryPositionEnum(position)
        for position in range(
            CharacterInventoryPositionEnum.InventoryPositionDofus1,
            CharacterInventoryPositionEnum.InventoryPositionDofus6 + 1,
        )
    ),
    82: (CharacterInventoryPositionEnum.AccessoryPositionShield,),
}


def _roll_weight_by_characteristic(primary_elem: EffectElement) -> dict[int, float]:
    element_info = ELEMENT_INFO_BY_ID[primary_elem]
    weights = dict(_BASE_ROLL_WEIGHT)
    weights[element_info.flat_damage_bonus] = _PRIMARY_FLAT_DAMAGE_WEIGHT
    weights[element_info.scaling_stat] = _PRIMARY_SCALING_WEIGHT
    return weights


def roll_score(object_item: ObjectItemInventory, primary_elem: EffectElement) -> float:
    weights = _roll_weight_by_characteristic(primary_elem)
    effect_by_id = DataReader().effect_by_id
    return sum(
        weights.get(
            effect_by_id[effect.action].characteristic if effect.action in effect_by_id else -1,
            _DEFAULT_ROLL_WEIGHT,
        )
        * effect.value_int
        for effect in object_item.item.effects
    )


def get_equipment_positions(item_gid: int) -> tuple[CharacterInventoryPositionEnum, ...]:
    item_type_id = DataReader().item_by_id[item_gid].typeId
    if item_type_id in _WEAPON_TYPE_IDS:
        return (CharacterInventoryPositionEnum.AccessoryPositionWeapon,)
    return _EQUIPMENT_POSITIONS_BY_TYPE_ID.get(item_type_id, ())


def equipment_score(object_items: Iterable[ObjectItemInventory], primary_elem: EffectElement) -> float:
    items = list(object_items)
    score = sum(roll_score(item, primary_elem) for item in items)
    item_by_id = DataReader().item_by_id
    pieces_by_set: Counter[int] = Counter()
    for item in items:
        item_data = item_by_id.get(item.item.gid)
        if item_data is not None and item_data.itemSetId is not None and item_data.itemSetId > 0:
            pieces_by_set[item_data.itemSetId] += 1
    weights = _roll_weight_by_characteristic(primary_elem)
    effect_by_id = DataReader().effect_by_id
    for set_id, pieces in pieces_by_set.items():
        bonuses: list[list[tuple[int, int]]] = DataReader().item_set_effects_by_id.get(set_id, [])
        if pieces >= len(bonuses):
            continue
        for action, value in bonuses[pieces]:
            characteristic = effect_by_id[action].characteristic if action in effect_by_id else -1
            score += weights.get(characteristic, _DEFAULT_ROLL_WEIGHT) * value
    return score


def get_best_roll(
    object_items: Iterable[ObjectItemInventory], primary_elem: EffectElement
) -> ObjectItemInventory | None:
    return max(
        object_items,
        key=lambda object_item: roll_score(object_item, primary_elem),
        default=None,
    )


def get_current_best_set(elem: EffectElement, level: int, is_sub: bool) -> set_infos.SetOnLevel | None:
    available_set = [
        set_on_level
        for set_on_level in set_infos.SET_BY_LEVEL_THRESHOLD
        if set_on_level.min_level <= level
        and (set_on_level.min_level <= 60 or is_sub)
        and set_on_level.elem == elem
    ]
    if not available_set:
        return None

    best_available_set = max(available_set, key=lambda set_on_level: set_on_level.min_level)
    return best_available_set


def get_item_gids_to_buy(
    set: set_infos.SetOnLevel, object_by_uid: dict[int, ObjectItemInventory]
) -> list[ItemToBuyInfo]:

    item_info_to_buy: list[ItemToBuyInfo] = []
    for position, item_info in set.item_info_by_position.items():
        equipped_item = get_equipment_on_position(object_by_uid, position)
        if not equipped_item or equipped_item.item.gid != item_info.item_gid:
            item_info_to_buy.append(item_info)

    return item_info_to_buy
