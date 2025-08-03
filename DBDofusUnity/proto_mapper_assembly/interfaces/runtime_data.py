from __future__ import annotations

from pydantic import BaseModel, RootModel

type NormalizedRuntimeInstance = dict[str, object]


class RuntimeInstance(BaseModel, extra="allow"):
    from_server: bool | None
    is_game_msg: bool
    is_root_msg: bool
    capture_sequence: int | None
    capture_session_id: str | None = None


class RuntimeRoot(RootModel[dict[str, tuple[RuntimeInstance, ...]]]):
    root: dict[str, tuple[RuntimeInstance, ...]]


class ObservedRootObfMessage(BaseModel):
    """One obfuscated root message the captures prove exists, summarised for reporting."""

    obf_msg_namespace: str
    from_server: bool | None
    instance_count: int
    observed_field_names: tuple[str, ...]

    def describe(self) -> str:
        direction = "server" if self.from_server else "client"
        return (
            f"{self.obf_msg_namespace} ({direction}, {self.instance_count} captures, "
            f"{len(self.observed_field_names)} fields)"
        )
