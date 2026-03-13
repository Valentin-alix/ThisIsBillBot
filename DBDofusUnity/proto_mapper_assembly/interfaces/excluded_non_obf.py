from pydantic import RootModel, model_validator


class ExcludedNonObfConfig(RootModel[list[str]]):
    @model_validator(mode="after")
    def validate_unique_exclusions(self) -> "ExcludedNonObfConfig":
        if len(self.root) != len(set(self.root)):
            raise ValueError("Duplicate message in the non-obf exclusion list")
        return self
