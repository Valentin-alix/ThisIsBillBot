from datetime import datetime
from enum import StrEnum
from typing import Annotated, Literal, Mapping

from pydantic import BaseModel, Field

Percentage = Annotated[float, Field(ge=0, le=1.0000001)]


class BaseMappingInfo(BaseModel):
    obf_msg_namespace: str


class RejectionReason(StrEnum):
    TYPE_MISMATCH = "type_mismatch"
    CARDINALITY_MISMATCH = "cardinality_mismatch"
    VALIDATOR_FAILURE = "validator_failure"
    FORCED_NON_MATCH = "forced_non_match"
    NOT_SELECTED = "not_selected"


type FieldMapping = Mapping[
    str, tuple[float, str, MappingInfo | None, RejectionReason | None] | None
]


class MappingInfo(BaseModel):
    clear_msg_namespace: str
    similarity: Percentage
    field_mapping: FieldMapping


type OutputFieldMapping = dict[str, str | None]


class OutputMappingInfo(BaseMappingInfo):
    field_mapping: OutputFieldMapping


class AlternativeCandidate(BaseModel):
    clear_field: str
    similarity: Percentage
    reliability: float
    rejection_reason: RejectionReason


class FieldAuditInfo(BaseModel):
    matched_clear_field: str | None
    similarity: Percentage
    reliability: float
    source: Literal["calculated", "forced"]
    alternatives: list[AlternativeCandidate]


class MessageAuditInfo(BaseModel):
    similarity: Percentage
    algorithm: Literal["hungarian", "pulp"]
    validator_priority: int
    fields: dict[str, FieldAuditInfo]


class AuditHeader(BaseModel):
    generated_at: datetime
    metrics: dict[str, int | float]


class MappingAudit(BaseModel):
    header: AuditHeader = Field(alias="_header")
    messages: dict[str, MessageAuditInfo]

    class Config:
        populate_by_name = True
