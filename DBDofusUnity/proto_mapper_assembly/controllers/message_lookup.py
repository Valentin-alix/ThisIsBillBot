from collections import defaultdict
from collections.abc import Mapping

from DBDofusUnity.proto_mapper_assembly.helpers.non_obf_names import (
    build_filtered_message_namespace,
    build_pinned_non_obf_name,
)
from DBDofusUnity.proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessage


def resolve_obf_alias(alias: str, alias_to_cls: Mapping[str, frozenset[str]]) -> str:
    candidates = alias_to_cls.get(alias)
    if not candidates:
        return alias
    if len(candidates) != 1:
        sorted_candidates = ", ".join(sorted(candidates))
        message = f"Ambiguous pinned obf message alias {alias!r}: {sorted_candidates}"
        raise ValueError(message)
    return next(iter(candidates))


def resolve_non_obf_alias(
    alias: str, alias_to_cls: Mapping[str, frozenset[str]], short_alias_to_cls: Mapping[str, frozenset[str]]
) -> str:
    candidates = alias_to_cls.get(alias)
    if not candidates:
        candidates = short_alias_to_cls.get(alias)
    if not candidates:
        message = f"Unknown non-obf message alias: {alias!r}"
        raise ValueError(message)
    if alias in candidates:
        return alias
    if len(candidates) != 1:
        sorted_candidates = ", ".join(sorted(candidates))
        message = f"Ambiguous non-obf message alias {alias!r}: {sorted_candidates}"
        raise ValueError(message)
    return next(iter(candidates))


def build_non_obf_alias_lookup(
    *, non_obf_messages_by_cls: Mapping[str, DumpCSMessage]
) -> tuple[dict[str, frozenset[str]], dict[str, frozenset[str]]]:
    alias_to_cls: dict[str, set[str]] = defaultdict(set)
    short_alias_to_cls: dict[str, set[str]] = defaultdict(set)
    for message_cls, message in non_obf_messages_by_cls.items():
        alias_to_cls[build_pinned_non_obf_name(message=message, messages_by_cls=non_obf_messages_by_cls)].add(
            message_cls
        )
        short_alias_to_cls[message.name].add(message_cls)

    return {alias: frozenset(candidates) for alias, candidates in alias_to_cls.items()}, {
        alias: frozenset(candidates) for alias, candidates in short_alias_to_cls.items()
    }


def build_obf_alias_lookup(
    *,
    obf_messages_by_cls: Mapping[str, DumpCSMessage],
) -> dict[str, frozenset[str]]:
    """Index exported namespaces without static containers so short-form pins resolve."""
    alias_to_cls: dict[str, set[str]] = defaultdict(set)
    for message_cls, message in obf_messages_by_cls.items():
        alias = build_filtered_message_namespace(
            is_obf=True, message=message, messages_by_cls=obf_messages_by_cls
        )
        alias_to_cls[alias].add(message_cls)
        alias_to_cls[message_cls].add(message_cls)
    return {alias: frozenset(candidates) for alias, candidates in alias_to_cls.items()}
