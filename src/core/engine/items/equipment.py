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
    # Action economy — dominant value
    CharacteristicEnum.ACTION_POINTS: 100.0,
    CharacteristicEnum.MOVEMENT_POINTS: 70.0,
    CharacteristicEnum.RANGE: 40.0,
    # Primary offense
    CharacteristicEnum.POWER: 3,
    CharacteristicEnum.ALL_DAMAGES_BONUS: 9,
    CharacteristicEnum.DAMAGES_FACTOR: 6,
    CharacteristicEnum.DAMAGES_PERCENT_SPELL: 6,
    # Secondary stats
    CharacteristicEnum.WISDOM: 1.5,
    CharacteristicEnum.VITALITY: 1.0,
}
_PRIMARY_FLAT_DAMAGE_WEIGHT = 9
_PRIMARY_SCALING_WEIGHT = 3
_OFF_PRIMARY_FLAT_DAMAGE_WEIGHT = _PRIMARY_FLAT_DAMAGE_WEIGHT / 25
_OFF_PRIMARY_SCALING_WEIGHT = _PRIMARY_SCALING_WEIGHT / 25
_DEFAULT_ROLL_WEIGHT = 0.01

_EQUIPMENT_POSITIONS_BY_TYPE_ID: dict[int, tuple[CharacterInventoryPositionEnum, ...]] = {
    1: (CharacterInventoryPositionEnum.AccessoryPositionAmulet,),
    **{
        item_type_id: (CharacterInventoryPositionEnum.AccessoryPositionWeapon,)
        for item_type_id in (2, 3, 4, 5, 6, 7, 8, 19, 20, 21, 22, 114, 271)
    },
    9: (
        CharacterInventoryPositionEnum.InventoryPositionRingLeft,
        CharacterInventoryPositionEnum.InventoryPositionRingRight,
    ),
    10: (CharacterInventoryPositionEnum.AccessoryPositionBelt,),
    11: (CharacterInventoryPositionEnum.AccessoryPositionBoots,),
    16: (CharacterInventoryPositionEnum.AccessoryPositionHat,),
    17: (CharacterInventoryPositionEnum.AccessoryPositionCape,),
    18: (CharacterInventoryPositionEnum.AccessoryPositionPets,),
    121: (CharacterInventoryPositionEnum.AccessoryPositionPets,),
    23: tuple(
        CharacterInventoryPositionEnum(position)
        for position in range(
            CharacterInventoryPositionEnum.InventoryPositionDofus1,
            CharacterInventoryPositionEnum.InventoryPositionDofus6 + 1,
        )
    ),
    82: (CharacterInventoryPositionEnum.AccessoryPositionShield,),
    151: tuple(
        CharacterInventoryPositionEnum(position)
        for position in range(
            CharacterInventoryPositionEnum.InventoryPositionDofus1,
            CharacterInventoryPositionEnum.InventoryPositionDofus6 + 1,
        )
    ),
    217: tuple(
        CharacterInventoryPositionEnum(position)
        for position in range(
            CharacterInventoryPositionEnum.InventoryPositionDofus1,
            CharacterInventoryPositionEnum.InventoryPositionDofus6 + 1,
        )
    ),
    311: (CharacterInventoryPositionEnum.InventoryPositionMount,),
    331: (CharacterInventoryPositionEnum.InventoryPositionMount,),
    332: (CharacterInventoryPositionEnum.InventoryPositionMount,),
    333: (CharacterInventoryPositionEnum.InventoryPositionMount,),
}


def _roll_weight_by_characteristic(primary_elem: EffectElement) -> dict[int, float]:
    weights = dict(_BASE_ROLL_WEIGHT)
    for elem_id, element_info in ELEMENT_INFO_BY_ID.items():
        is_primary = elem_id == primary_elem
        flat_weight = _PRIMARY_FLAT_DAMAGE_WEIGHT if is_primary else _OFF_PRIMARY_FLAT_DAMAGE_WEIGHT
        scaling_weight = _PRIMARY_SCALING_WEIGHT if is_primary else _OFF_PRIMARY_SCALING_WEIGHT
        weights[element_info.flat_damage_bonus] = max(
            weights.get(element_info.flat_damage_bonus, 0.0), flat_weight
        )
        weights[element_info.scaling_stat] = max(weights.get(element_info.scaling_stat, 0.0), scaling_weight)
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
        if pieces > len(bonuses):
            continue
        for action, value in bonuses[pieces - 1]:
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
    set: set_infos.SetOnLevel,
    object_by_uid: dict[int, ObjectItemInventory],
    primary_elem: EffectElement,
) -> list[ItemToBuyInfo]:
    item_info_to_buy: list[ItemToBuyInfo] = []
    for position, item_info in set.item_info_by_position.items():
        equipped_item = get_equipment_on_position(object_by_uid, position)
        if equipped_item is None or equipped_item.item.gid == item_info.item_gid:
            if equipped_item is None:
                item_info_to_buy.append(item_info)
            continue

        owned_target = get_best_roll(
            (obj for obj in object_by_uid.values() if obj.item.gid == item_info.item_gid), primary_elem
        )
        if owned_target is None or roll_score(owned_target, primary_elem) > roll_score(
            equipped_item, primary_elem
        ):
            item_info_to_buy.append(item_info)

    return item_info_to_buy
