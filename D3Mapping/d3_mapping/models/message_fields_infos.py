from typing import Any

from pydantic import BaseModel

type ValueByField = dict[str, Any]


class ObfMessageInfo(BaseModel):
    value_by_field_array: ValueByField

    def __hash__(self) -> int:
        return self.value_by_field_array.values().__hash__()


class ParsedObfMessageInfos(BaseModel):
    obf_msg_info: list[ObfMessageInfo] = []
    from_server: bool
    is_entry_msg: bool
