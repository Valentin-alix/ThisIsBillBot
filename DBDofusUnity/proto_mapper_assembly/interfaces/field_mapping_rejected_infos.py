from typing import Literal

from pydantic import BaseModel, ConfigDict


class ValidationFailureRejectedInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reason: Literal["validation_failure"]
    value: object


class ScoreRejectedInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reason: Literal["not_selected"]
    score: float


class ReasonRejectedInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reason: str


type FieldMappingRejectedInfo = str | ValidationFailureRejectedInfo | ScoreRejectedInfo | ReasonRejectedInfo
type FieldMappingRejectedInfos = dict[str, dict[str, FieldMappingRejectedInfo]]
