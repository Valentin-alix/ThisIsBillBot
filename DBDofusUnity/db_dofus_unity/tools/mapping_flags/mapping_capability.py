import json
import os.path
from collections import defaultdict
from functools import reduce
from pathlib import Path

from D3Database.data_center.data_reader import DataReader

CAPABILITY_ALLOW_CHALLENGE: int = 1
CAPABILITY_ALLOW_AGGRESSION: int = 2
CAPABILITY_ALLOW_TELEPORT_TO: int = 4
CAPABILITY_ALLOW_TELEPORT_FROM: int = 8
CAPABILITY_ALLOW_EXCHANGES_BETWEEN_PLAYERS: int = 16
CAPABILITY_ALLOW_HUMAN_VENDOR: int = 32
CAPABILITY_ALLOW_COLLECTOR: int = 64
CAPABILITY_ALLOW_SOUL_CAPTURE: int = 128
CAPABILITY_ALLOW_SOUL_SUMMON: int = 256
CAPABILITY_ALLOW_TAVERN_REGEN: int = 512
CAPABILITY_ALLOW_TOMB_MODE: int = 1024
CAPABILITY_ALLOW_TELEPORT_EVERYWHERE: int = 2048
CAPABILITY_ALLOW_FIGHT_CHALLENGES: int = 4096
CAPABILITY_ALLOW_MONSTER_RESPAWN: int = 8192
CAPABILITY_ALLOW_MONSTER_FIGHT: int = 16384
CAPABILITY_ALLOW_MOUNT: int = 32768
CAPABILITY_ALLOW_OBJECT_DISPOSAL: int = 65536
CAPABILITY_ALLOW_UNDERWATER: int = 131072
CAPABILITY_ALLOW_PVP_1V1: int = 262144
CAPABILITY_ALLOW_PVP_3V3: int = 524288
CAPABILITY_ALLOW_MONSTER_AGRESSION: int = 1048576


def does_allow_capability(capability: int, check: int):
    return (capability & check) != 0


def map_capability():
    with open(
        os.path.join(Path(__file__).parent, "resources", "MapPositions.json")
    ) as file:
        old_datas = json.load(file)
    old_capability_by_map_id = {data["id"]: data["capabilities"] for data in old_datas}

    allow_capability: dict[int, int] = defaultdict(int)
    not_allow_capability: dict[int, int] = defaultdict(int)
    for map_id, map_pos in DataReader().map_pos_by_map_id.items():
        old_capability = old_capability_by_map_id.get(map_id)
        if old_capability is None:
            continue
        if does_allow_capability(old_capability, CAPABILITY_ALLOW_MONSTER_AGRESSION):
            allow_capability[map_pos.m_flags] += 1
        else:
            not_allow_capability[map_pos.m_flags] += 1

    valuable_allow_capability = {
        key for key, value in allow_capability.items() if value > 10
    }
    valuable_not_allow_capability = {
        key for key, value in not_allow_capability.items() if value > 10
    }

    common_bits = reduce(
        lambda previous, flag: previous & flag, valuable_allow_capability
    )

    for value in valuable_not_allow_capability:
        if value & common_bits != 0:
            # Si un bit commun apparaît aussi dans values_without, il n'est pas caractéristique
            common_bits &= ~(value & common_bits)

    print(common_bits)


if __name__ == "__main__":
    map_capability()
