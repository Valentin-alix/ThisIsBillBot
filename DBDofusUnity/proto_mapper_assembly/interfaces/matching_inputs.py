from __future__ import annotations

from dataclasses import dataclass

from proto_mapper_assembly.interfaces.assembly_access import AccessTraceDocument, MessageAccessSignature
from proto_mapper_assembly.interfaces.capture_sequence_hints import CaptureSequenceHintsConfig
from proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessage
from proto_mapper_assembly.interfaces.enum_mapping import EnumSignatureEntry
from proto_mapper_assembly.interfaces.pinned_pairs import PinnedPairsConfig
from proto_mapper_assembly.interfaces.signature_overrides import SignatureOverrideEntry
from proto_mapper_assembly.runtime.runtime_store import RuntimeDataStore


@dataclass(frozen=True)
class MatchingInputs:
    """Everything derived from the two builds. Loaded together, immutable for the whole run."""

    obf_messages_by_cls: dict[str, DumpCSMessage]
    non_obf_messages_by_cls: dict[str, DumpCSMessage]
    obf_signatures_by_cls: dict[str, MessageAccessSignature]
    non_obf_signatures_by_cls: dict[str, MessageAccessSignature]
    signature_overrides_by_non_obf_cls: dict[str, SignatureOverrideEntry]
    obf_enum_signatures_by_name: dict[str, EnumSignatureEntry]
    non_obf_enum_signatures_by_name: dict[str, EnumSignatureEntry]
    obf_access_trace: AccessTraceDocument
    non_obf_access_trace: AccessTraceDocument


@dataclass(frozen=True)
class MatchingRunConfig:
    """
    What steers one run, as opposed to what it is made of.

    Kept apart from ``MatchingInputs`` because these are loaded separately and later: pins and
    capture hints need the bootstrap messages to resolve their targets, and a replay can legitimately
    run with an era's pins and no hints at all.
    """

    runtime_data_store: RuntimeDataStore
    pinned_pairs_config: PinnedPairsConfig
    capture_sequence_hints_config: CaptureSequenceHintsConfig
