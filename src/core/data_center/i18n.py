import zlib

import msgspec

from D3Database.consts import D3_I18N

type I18NRoot = dict[int, str]


class I18N:
    with open(D3_I18N, "rb") as file:
        name_by_id = msgspec.json.decode(zlib.decompress(file.read()), type=I18NRoot)


if __name__ == "__main__":
    print(I18N.name_by_id)

    # for skill in DataReader().skill_names_by_id.values():
    #     icecream.ic(I18N().name_by_id[skill.nameId])
