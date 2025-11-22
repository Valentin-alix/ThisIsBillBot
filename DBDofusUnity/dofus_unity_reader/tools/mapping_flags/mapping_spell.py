import json
from collections import defaultdict
from functools import reduce
from pathlib import Path

from DBDofusUnity.dofus_unity_reader.data_center.data_reader import DataReader

_MIN_THRESHOLD: int = 15


def map_spell_level() -> None:
    resources = Path(__file__).parent / "resources" / "SpellLevels.json"
    with resources.open() as file:
        old_datas = json.load(file)
    old_value_by_spell_lvl_id = {data["id"]: data["castTestLos"] for data in old_datas}

    count_flags_verified: dict[int, int] = defaultdict(int)
    for spell_levels in DataReader().spell_lvl_by_spell_id.values():
        for spell_lvl in spell_levels:
            old_value = old_value_by_spell_lvl_id.get(spell_lvl.id)
            if old_value is None:
                continue
            if old_value is True:
                count_flags_verified[spell_lvl.m_flags] += 1

    valids = [flag for flag, count in count_flags_verified.items() if count > _MIN_THRESHOLD]
    print(valids)
    res = reduce(lambda previous, flag: previous & flag, valids)
    print(res)

    # castInLine -> 1
    # castInDiag -> 2
    # castTestLos -> 4
    # needTakenCell -> 16
    # rangeCanBeBoosted -> 64


if __name__ == "__main__":
    map_spell_level()
