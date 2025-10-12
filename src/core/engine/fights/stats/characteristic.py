from DBDofusUnity.datas.protos.non_obf.game.character_pb2 import (
    CharacterCharacteristicUpgradeRequest,
)
from DBDofusUnity.datas.protos.non_obf.game.common_pb2 import (
    CharacterCharacteristic,
)
from DBDofusUnity.dofus_unity_reader.game_constants.characteristic import EffectElement


def get_stat_by_id(stat: CharacterCharacteristic | None) -> int:
    if stat is None:
        return 0
    if stat.HasField("detailed"):
        return (
            stat.detailed.base
            + stat.detailed.additional
            + stat.detailed.objects_and_mount_bonus
            + stat.detailed.alignment_gift_bonus
            + stat.detailed.context_modification
            + stat.detailed.temporary
        )
    elif stat.HasField("usable"):
        return (
            stat.usable.base
            + stat.usable.objects_and_mount_bonus
            + stat.usable.alignment_gift_bonus
            + stat.usable.additional
            + stat.usable.context_modification
            + stat.usable.temporary
        )
    elif stat.HasField("value"):
        return stat.value.total

    return 0


def get_max_characteristic_per_point(level: int) -> int:
    available_points = (level - 1) * 5

    used_points = 0
    remaining = available_points

    take = min(100, remaining // 1)
    used_points += take * 1
    remaining -= take * 1

    take = min(100, remaining // 2)
    used_points += take * 2
    remaining -= take * 2

    take = min(100, remaining // 3)
    used_points += take * 3
    remaining -= take * 3

    take = remaining // 4
    used_points += take * 4
    remaining -= take * 4

    return used_points


def build_characteristic_upgrade_request(
    primary_element: EffectElement, points: int
) -> CharacterCharacteristicUpgradeRequest:
    match primary_element:
        case EffectElement.STRENGTH:
            return CharacterCharacteristicUpgradeRequest(strength=points)
        case EffectElement.INTELLIGENCE:
            return CharacterCharacteristicUpgradeRequest(intelligence=points)
        case EffectElement.CHANCE:
            return CharacterCharacteristicUpgradeRequest(chance=points)
        case _:
            return CharacterCharacteristicUpgradeRequest(agility=points)
