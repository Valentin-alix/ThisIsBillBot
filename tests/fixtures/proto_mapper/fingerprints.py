from dataclasses import dataclass, field


def _new_string_list() -> list[str]:
    return []


def _new_field_fingerprints() -> "list[FieldFingerprint]":
    return []


@dataclass
class FieldFingerprint:
    field_name: str = ""


@dataclass
class MessageFingerprint:
    name: str = "Message"
    namespace: str | None = None
    parent_name: str | None = None
    field_signatures: list[str] = field(default_factory=_new_string_list)
    field_fingerprints: list[FieldFingerprint] = field(default_factory=_new_field_fingerprints)

    @property
    def composed_name(self) -> str:
        if self.parent_name is not None:
            return f"{self.parent_name}.{self.name}"
        if self.namespace is not None:
            return f"{self.namespace}.{self.name}"
        return self.name

    def __hash__(self) -> int:
        return hash(self.composed_name)


def field_fingerprint(*, field_name: str = "") -> FieldFingerprint:
    return FieldFingerprint(field_name=field_name)


def message_fingerprint(
    *,
    name: str = "Message",
    namespace: str | None = None,
    parent_name: str | None = None,
    field_signatures: list[str] | None = None,
) -> MessageFingerprint:
    return MessageFingerprint(
        name=name,
        namespace=namespace,
        parent_name=parent_name,
        field_signatures=list(field_signatures or []),
    )
