from functools import cached_property

import msgspec
from base_python.singleton import Singleton

from DBDofusUnity.consts import I18N_OUTPUT_PATH

I18NRoot = dict[int, str]


class I18N(metaclass=Singleton):
    @cached_property
    def name_by_id(self) -> I18NRoot:
        with I18N_OUTPUT_PATH.open("rb") as file:
            return msgspec.json.decode(file.read(), type=I18NRoot)

    @cached_property
    def id_by_name(self) -> dict[str, int]:
        return {name: name_id for name_id, name in self.name_by_id.items()}
