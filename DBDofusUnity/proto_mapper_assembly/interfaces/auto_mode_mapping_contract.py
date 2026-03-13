from pydantic import BaseModel, Field, model_validator


class AutoModeMappingThresholds(BaseModel):
    message_score: float = Field(ge=0.0, le=1.0)
    match_margin: float = Field(ge=0.0, le=1.0)
    field_score: float = Field(ge=0.0, le=1.0)


class AutoModeMessageRequirement(BaseModel):
    message: str = Field(min_length=1)
    fields: list[str] = Field(default_factory=list[str])
    activities: list[str] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_unique_values(self) -> "AutoModeMessageRequirement":
        if len(self.fields) != len(set(self.fields)):
            raise ValueError(f"Duplicate field in requirement for {self.message}")
        if len(self.activities) != len(set(self.activities)):
            raise ValueError(f"Duplicate activity in requirement for {self.message}")
        return self


class AutoModeMappingContract(BaseModel):
    version: int = Field(ge=1)
    thresholds: AutoModeMappingThresholds
    messages: list[AutoModeMessageRequirement] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_unique_messages(self) -> "AutoModeMappingContract":
        normalized_messages = [_normalize_name(requirement.message) for requirement in self.messages]
        if len(normalized_messages) != len(set(normalized_messages)):
            raise ValueError("Duplicate message in auto-mode mapping contract")
        return self


def _normalize_name(value: str) -> str:
    return value.removeprefix(".").casefold()
