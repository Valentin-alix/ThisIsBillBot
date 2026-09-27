from typing import Self

from pydantic import BaseModel, RootModel, model_validator

type NormalizedRuntimeInstance = dict[str, object]


class RuntimeInstance(BaseModel, extra="allow"):
    from_server: bool | None
    is_game_msg: bool
    is_root_msg: bool
    capture_sequence: int | None
    capture_session_id: str | None = None

    @model_validator(mode="after")
    def validate_root_direction(self) -> Self:
        if self.is_root_msg and not self.is_game_msg and self.from_server is None:
            raise ValueError("Captured root payloads require from_server")
        return self


class RuntimeRoot(RootModel[dict[str, tuple[RuntimeInstance, ...]]]):
    root: dict[str, tuple[RuntimeInstance, ...]]


class RuntimeCaptureDocument(BaseModel):
    schema_fingerprint: str
    root: dict[str, tuple[RuntimeInstance, ...]]


class ObservedRootObfMessage(BaseModel):
    obf_msg_namespace: str
    from_server: bool | None
    instance_count: int
    observed_field_names: tuple[str, ...]
    capture_session_ids: tuple[str, ...] = ()

    def describe(self) -> str:
        direction = "server" if self.from_server else "client"
        session_label = "session" if len(self.capture_session_ids) == 1 else "sessions"
        return (
            f"{self.obf_msg_namespace} ({direction}, {self.instance_count} captures, "
            f"{len(self.observed_field_names)} fields, {len(self.capture_session_ids)} {session_label})"
        )
