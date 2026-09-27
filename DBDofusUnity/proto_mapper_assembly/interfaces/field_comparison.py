from typing import Literal, NamedTuple

from pydantic import BaseModel, Field, model_validator


type ComparisonPredicate = Literal["eq", "lt", "le", "gt", "ge"]


class FieldComparisonKey(NamedTuple):
    predicate: ComparisonPredicate
    constant: int
    width: int
    signed: bool | None


class FieldComparison(BaseModel):
    predicate: ComparisonPredicate
    constant: int
    width: Literal[8, 16, 32, 64]
    signed: bool | None
    instruction_address: int = Field(ge=0)

    @model_validator(mode="after")
    def validate_signedness(self) -> "FieldComparison":
        if (self.predicate == "eq") != (self.signed is None):
            raise ValueError("Equality is unsigned-neutral; order comparisons require signedness.")
        return self

    @property
    def similarity_key(self) -> FieldComparisonKey:
        return FieldComparisonKey(self.predicate, self.constant, self.width, self.signed)
