from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

from DBDofusUnity.proto_mapper_assembly.controllers.message_lookup import (
    build_non_obf_alias_lookup,
    resolve_non_obf_alias,
)
from DBDofusUnity.proto_mapper_assembly.interfaces.capture_sequence_hints import (
    CaptureSequence,
    CaptureSequenceHintsConfig,
)
from DBDofusUnity.proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessage


def load_capture_sequence_hints(path: Path) -> CaptureSequenceHintsConfig:
    return CaptureSequenceHintsConfig.model_validate_json(path.read_text(encoding="utf-8"))


def resolve_capture_sequence_hints_non_obf_targets(
    *,
    capture_sequence_hints: CaptureSequenceHintsConfig,
    non_obf_messages_by_cls: Mapping[str, DumpCSMessage],
) -> CaptureSequenceHintsConfig:
    non_obf_alias_to_cls, short_non_obf_alias_to_cls = build_non_obf_alias_lookup(
        non_obf_messages_by_cls=non_obf_messages_by_cls
    )
    resolved_sequences = tuple(
        CaptureSequence(
            name=sequence.name,
            messages=tuple(
                resolve_non_obf_alias(
                    message_alias,
                    non_obf_alias_to_cls,
                    short_non_obf_alias_to_cls,
                )
                for message_alias in sequence.messages
            ),
        )
        for sequence in capture_sequence_hints.sequences
    )
    return CaptureSequenceHintsConfig(sequences=resolved_sequences)
