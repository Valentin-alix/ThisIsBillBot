import math
from d3_mapping.resources.protos.game.common_pb2 import CharacterCharacteristic


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
    chance = 0
    total_points = (level - 1) * 5

    while total_points > 0:
        if chance < 100:
            coeff = 1
        elif chance < 200:
            coeff = 2
        elif chance < 300:
            coeff = 3
        else:
            coeff = 4
        taken_points = min(total_points, 100)
        chance += taken_points / coeff
        total_points -= taken_points
        chance += total_points / coeff

    chance = math.floor(chance)
    return chance
