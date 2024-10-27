from typing import Any

from pydantic import BaseModel, ConfigDict

type ValueByField = dict[str, Any]


class ObfMessageInfo(BaseModel):
    model_config = ConfigDict(frozen=True)

    value_by_field_array: ValueByField

    def __init__(self, **data):
        super().__init__(**data)
        self._cached_hash = hash(self._dict_to_immutable(self.value_by_field_array))

    def __hash__(self):
        return self._cached_hash

    @staticmethod
    def _dict_to_immutable(_dict: dict) -> tuple:
        def convert(value: Any) -> Any:
            if isinstance(value, dict):
                return ObfMessageInfo._dict_to_immutable(value)
            elif isinstance(value, list):
                return tuple(convert(sub_value) for sub_value in value)
            else:
                return value

        return tuple(sorted((key, convert(value)) for key, value in _dict.items()))


class ParsedObfMessageInfos(BaseModel):
    obf_msg_info: set[ObfMessageInfo] = set()
    from_server: bool
    is_entry_msg: bool
