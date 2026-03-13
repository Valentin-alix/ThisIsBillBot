from pydantic import BaseModel, Field, model_validator


class CaptureSequence(BaseModel):
    name: str
    messages: tuple[str, ...] = Field(min_length=2)


class CaptureSequenceHintsConfig(BaseModel):
    sequences: tuple[CaptureSequence, ...]

    @model_validator(mode="after")
    def validate_sequence_names(self) -> "CaptureSequenceHintsConfig":
        sequence_names = [sequence.name for sequence in self.sequences]
        if len(set(sequence_names)) != len(sequence_names):
            message = "Capture sequence names must be unique"
            raise ValueError(message)
        return self
