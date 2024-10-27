import json
import os.path
from collections import defaultdict
from functools import reduce
from pathlib import Path

from data_center.i18n import I18N

from D3Database.data_center.data_reader import DataReader


def map_item():
    with open(os.path.join(Path(__file__).parent, "resources", "Item.json")) as file:
        old_datas = json.load(file)
    old_value_by_item_id = {data["id"]: data["isExchangeable"] for data in old_datas}

    count_flags_verified: dict[int, int] = defaultdict(int)
    for item in DataReader().item_by_id.values():
        old_value = old_value_by_item_id.get(item.id)
        if old_value is None:
            continue
        if old_value is True:
            name_item = I18N().name_by_id[
                DataReader().item_by_id[item.id or 0].nameId or 0
            ]
            print(name_item)
            count_flags_verified[item.m_flags] += 1

    valids = [flag for flag, count in count_flags_verified.items() if count > 15]
    print(valids)
    res = reduce(lambda previous, flag: previous & flag, valids)
    print(res)


if __name__ == "__main__":
    map_item()
