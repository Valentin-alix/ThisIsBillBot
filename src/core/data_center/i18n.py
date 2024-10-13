import zlib

import msgspec

from D3Database.consts import D3_I18N

I18NRoot = dict[int, str]


class I18N:
    with open(D3_I18N, "rb") as file:
        name_by_id = msgspec.json.decode(zlib.decompress(file.read()), type=I18NRoot)
