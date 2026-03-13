from typing import cast

from DBDofusUnity.datas.protos.non_obf.game.bak_pb2 import BidAction
from DBDofusUnity.dofus_unity_reader.data_center.data_reader import DataReader
from DBDofusUnity.dofus_unity_reader.grid.map_point import MapPoint
from DBDofusUnity.proto_mapper_assembly.validators.field_validators import (
    MAX_DOFUS_LEVEL,
    MAX_TURN_TIME_MS,
)

_MAX_ANGRY_TO_ATTACK_DELAY_MS = 24 * 60 * 60 * 1000
_CHARACTERISTIC_UPGRADE_FIELD_NAMES = (
    "strength",
    "vitality",
    "wisdom",
    "chance",
    "agility",
    "intelligence",
)
_ELEMENTAL_CHARACTERISTIC_FIELD_NAMES = frozenset({"strength", "chance", "agility", "intelligence"})


_MAX_CHARACTERISTIC_UPGRADE_POINTS = (MAX_DOFUS_LEVEL - 1) * 5
_VALID_ELEMENTAL_UPGRADE_POINTS = (
    frozenset(range(1, 101))
    | frozenset(100 + characteristic_points * 2 for characteristic_points in range(1, 101))
    | frozenset(300 + characteristic_points * 3 for characteristic_points in range(1, 101))
    | frozenset(
        600 + characteristic_points * 4
        for characteristic_points in range(1, _MAX_CHARACTERISTIC_UPGRADE_POINTS // 4 + 1)
        if 600 + characteristic_points * 4 <= _MAX_CHARACTERISTIC_UPGRADE_POINTS
    )
)


def _get_next_characteristic_point_cost(field_name: str, upgrade: int) -> int:
    if field_name == "vitality":
        return 1
    if field_name == "wisdom":
        return 3
    assert field_name in _ELEMENTAL_CHARACTERISTIC_FIELD_NAMES
    if upgrade < 100:
        return 1
    if upgrade < 300:
        return 2
    if upgrade < 600:
        return 3
    return 4


def validator_update_life_points_event(values: dict[str, object]) -> bool:
    max_lp = values["max_life_points"]
    life_pts = values["life_points"]
    assert isinstance(max_lp, int)
    assert isinstance(life_pts, int)
    return max_lp >= life_pts


def validator_exchange_first_character_pods(values: dict[str, object]) -> bool:
    first_max = values["first_character_max_weight"]
    first_cur = values["first_character_current_weight"]
    assert isinstance(first_max, int)
    assert isinstance(first_cur, int)
    return first_max >= first_cur


def validator_exchange_second_character_pods(values: dict[str, object]) -> bool:
    second_max = values["second_character_max_weight"]
    second_cur = values["second_character_current_weight"]
    assert isinstance(second_max, int)
    assert isinstance(second_cur, int)
    return second_max >= second_cur


def _cell_pair_within_short_distance(cell_a: int, cell_b: int) -> bool:
    return MapPoint.from_cell_id(cell_a).distance_to_map_point(MapPoint.from_cell_id(cell_b)) < 10


def validator_slide(values: dict[str, object]) -> bool:
    start = values["start_cell"]
    end = values["end_cell"]
    assert isinstance(start, int)
    assert isinstance(end, int)
    return start != end


def validator_exchange_positions(values: dict[str, object]) -> bool:
    caster = values["caster_cell_id"]
    target = values["target_cell_id"]
    assert isinstance(caster, int)
    assert isinstance(target, int)
    if caster == target:
        return False
    return _cell_pair_within_short_distance(caster, target)


def validator_character_characteristic_detailed_usable(values: dict[str, object]) -> bool:
    used = values["used"]
    base = values["base"]
    objects_bonus = values["objects_and_mount_bonus"]
    assert isinstance(used, int)
    assert isinstance(base, int)
    assert isinstance(objects_bonus, int)

    return used <= base + objects_bonus


def validator_exchange_requested_trade_event(values: dict[str, object]) -> bool:
    source_id = values["source_id"]
    target_id = values["target_id"]
    assert isinstance(source_id, int)
    assert isinstance(target_id, int)
    if source_id <= 0:
        return False
    if target_id <= 0:
        return False
    return source_id != target_id


def validator_character_characteristics(values: dict[str, object]) -> bool:
    floor = values["experience_level_floor"]
    next_floor = values["experience_next_level_floor"]
    assert isinstance(floor, int)
    assert isinstance(next_floor, int)
    if next_floor <= floor:
        return False
    exp = values["experience"]
    assert isinstance(exp, int)
    return floor <= exp <= next_floor


def validator_job_experience(values: dict[str, object]) -> bool:
    floor = values["job_xp_level_floor"]
    next_floor = values["job_xp_next_level_floor"]
    exp = values["job_xp"]
    assert isinstance(floor, int)
    assert isinstance(next_floor, int)
    assert isinstance(exp, int)
    return floor <= exp <= next_floor


def validator_fight_starting_positions(values: dict[str, object]) -> bool:
    challengers = values["challengers_positions"]
    defenders = values["defenders_positions"]

    assert isinstance(challengers, list)
    assert isinstance(defenders, list)

    return not (set(cast("list[int]", challengers)) & set(cast("list[int]", defenders)))


def validator_map_coordinates(values: dict[str, object]) -> bool:
    world_x = values["world_x"]
    world_y = values["world_y"]
    assert isinstance(world_x, int)
    assert isinstance(world_y, int)
    return (world_x, world_y) in DataReader().map_pos_by_coord


def validator_paddock_move_item_request(values: dict[str, object]) -> bool:
    old_cell_id = values["old_cell_id"]
    new_cell_id = values["new_cell_id"]
    assert isinstance(old_cell_id, int)
    assert isinstance(new_cell_id, int)
    return old_cell_id != new_cell_id


def validator_paddocks_to_sell_event(values: dict[str, object]) -> bool:
    page_index = values["page_index"]
    page_total = values["page_total"]
    assert isinstance(page_index, int)
    assert isinstance(page_total, int)
    return page_index <= page_total


def _validator_distinct_ids(values: dict[str, object], left: str, right: str) -> bool:
    left_id = values[left]
    right_id = values[right]
    assert isinstance(left_id, int)
    assert isinstance(right_id, int)
    return left_id != right_id


def validator_aggression_event(values: dict[str, object]) -> bool:
    return _validator_distinct_ids(values, "attacker_id", "defender_id")


def validator_fight_request_canceled_event(values: dict[str, object]) -> bool:
    return _validator_distinct_ids(values, "source_id", "target_id")


def validator_player_fight_friendly_requested_event(values: dict[str, object]) -> bool:
    return _validator_distinct_ids(values, "source_id", "target_id")


def validator_player_fight_friendly_answered_event(values: dict[str, object]) -> bool:
    return _validator_distinct_ids(values, "source_id", "target_id")


def validator_monster_angry_at_player_event(values: dict[str, object]) -> bool:
    angry_start_time = values["angry_start_time"]
    attack_time = values["attack_time"]
    assert isinstance(angry_start_time, int)
    assert isinstance(attack_time, int)
    if attack_time < angry_start_time:
        return False
    return attack_time - angry_start_time <= _MAX_ANGRY_TO_ATTACK_DELAY_MS


def validator_fight_slave_switch_context_event(values: dict[str, object]) -> bool:
    return _validator_distinct_ids(values, "master_id", "slave_id")


def validator_fight_turn_event(values: dict[str, object]) -> bool:
    base_time = values["base_time"]
    extra_time = values["extra_time"]
    assert isinstance(base_time, int)
    assert isinstance(extra_time, int)
    return base_time + extra_time <= MAX_TURN_TIME_MS


def validator_paddock_buy_result_event(values: dict[str, object]) -> bool:
    bought = values["bought"]
    price = values["price"]
    assert isinstance(bought, bool)
    assert isinstance(price, int)
    return price > 0


def validator_subscribe_multiple_channel_request(values: dict[str, object]) -> bool:
    channel_enabled = values["channel_enabled"]
    channel_disabled = values["channel_disabled"]
    assert isinstance(channel_enabled, list)
    assert isinstance(channel_disabled, list)
    enabled_channels = set(cast("list[int]", channel_enabled))
    disabled_channels = set(cast("list[int]", channel_disabled))
    return bool(enabled_channels or disabled_channels) and not enabled_channels & disabled_channels


def _is_buy_ogrine_action(value: object) -> bool:
    return value == BidAction.BID_BUY_OGRINE or value == "BID_BUY_OGRINE"


def validator_bak_action_request(values: dict[str, object]) -> bool:
    if not _is_buy_ogrine_action(values["bid_action"]):
        return True
    kamas = values["kamas"]
    ogrines = values["ogrines"]
    rate = values["rate"]
    assert isinstance(kamas, int)
    assert isinstance(ogrines, int)
    assert isinstance(rate, int)
    return kamas == ogrines * rate


def validator_bak_action_event(values: dict[str, object]) -> bool:
    if not _is_buy_ogrine_action(values["bid_action"]):
        return True
    kamas = values["kamas"]
    amount = values["amount"]
    rate = values["rate"]
    assert isinstance(kamas, int)
    assert isinstance(amount, int)
    assert isinstance(rate, int)
    return kamas == amount * rate


def validator_character_characteristic_upgrade_request(values: dict[str, object]) -> bool:
    positive_upgrades: list[tuple[str, int]] = []
    for field_name in _CHARACTERISTIC_UPGRADE_FIELD_NAMES:
        upgrade = values[field_name]
        assert isinstance(upgrade, int)
        if upgrade < 0:
            return False
        if upgrade > 0:
            positive_upgrades.append((field_name, upgrade))

    if not positive_upgrades:
        return False

    for field_name, upgrade in positive_upgrades:
        if (
            field_name in _ELEMENTAL_CHARACTERISTIC_FIELD_NAMES
            and upgrade not in _VALID_ELEMENTAL_UPGRADE_POINTS
        ):
            return False
        if field_name == "wisdom" and upgrade % 3 != 0:
            return False

    total_upgrade = sum(upgrade for _, upgrade in positive_upgrades)
    if total_upgrade > _MAX_CHARACTERISTIC_UPGRADE_POINTS:
        return False
    available_points = ((total_upgrade + 4) // 5) * 5
    remaining_points = available_points - total_upgrade
    next_point_cost = min(
        _get_next_characteristic_point_cost(field_name, upgrade) for field_name, upgrade in positive_upgrades
    )
    return remaining_points < next_point_cost
