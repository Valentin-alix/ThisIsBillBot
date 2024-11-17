from typing import Annotated, Mapping

from pydantic import BaseModel, Field

Percentage = Annotated[float, Field(ge=0, le=1.0000001)]


class BaseMappingInfo(BaseModel):
    obf_msg_namespace: str


type FieldMapping = Mapping[str, tuple[float, str, MappingInfo | None] | None]


class MappingInfo(BaseModel):
    clear_msg_namespace: str
    similarity: Percentage
    field_mapping: FieldMapping


type OutputFieldMapping = dict[str, str | None]


class OutputMappingInfo(BaseMappingInfo):
    field_mapping: OutputFieldMapping
