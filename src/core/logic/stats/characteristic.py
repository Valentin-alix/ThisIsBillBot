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
            + stat.usable.context_modification
            + stat.usable.additional
            + stat.usable.objects_and_mount_bonus
        )
    elif stat.HasField("value"):
        return stat.value.total

    return 0
