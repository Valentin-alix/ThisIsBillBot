from pydantic import BaseModel

from d3_mapping.utils import Percentage


type FieldMapping = dict[str, tuple[str | None, Percentage]]


class MappingInfo(BaseModel):
    clear_msg_name: str
    similarity: Percentage
    field_mapping: FieldMapping
