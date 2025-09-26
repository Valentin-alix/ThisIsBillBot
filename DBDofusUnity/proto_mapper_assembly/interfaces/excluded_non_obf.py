from __future__ import annotations

from pydantic import RootModel, model_validator


class ExcludedNonObfConfig(RootModel[list[str]]):
    """Composed non-obfuscated dump.cs names absent from ``non_obf/game``."""

    @model_validator(mode="after")
    def validate_unique_exclusions(self) -> ExcludedNonObfConfig:
        if len(self.root) != len(set(self.root)):
            raise ValueError("Duplicate message in the non-obf exclusion list")
        return self
