from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessage
from proto_mapper_assembly.interfaces.excluded_non_obf import ExcludedNonObfConfig
from proto_mapper_assembly.interfaces.signature_overrides import SignatureOverrideEntry


def load_excluded_non_obf(path: Path) -> ExcludedNonObfConfig:
    if not path.exists():
        return ExcludedNonObfConfig(root=[])
    return ExcludedNonObfConfig.model_validate_json(path.read_text(encoding="utf-8"))


def split_excluded_non_obf_messages(
    *,
    messages: Sequence[DumpCSMessage],
    excluded_message_names: frozenset[str],
) -> tuple[list[DumpCSMessage], frozenset[str]]:
    """Split the messages into the ones to keep and the composed names that were dropped.

    The dropped names are needed to purge the stored signature overrides:
    an override left behind would be injected back as a synthetic message and undo the exclusion.
    """
    kept: list[DumpCSMessage] = []
    dropped: set[str] = set()
    for message in messages:
        if message.composed_name in excluded_message_names:
            dropped.add(message.composed_name)
        else:
            kept.append(message)
    return kept, frozenset(dropped)


def drop_excluded_signature_overrides(
    *,
    overrides: dict[str, SignatureOverrideEntry],
    dropped_message_names: frozenset[str],
) -> dict[str, SignatureOverrideEntry]:
    """Drop overrides whose exact composed class is excluded."""
    return {name: entry for name, entry in overrides.items() if name not in dropped_message_names}
