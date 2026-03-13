from dataclasses import dataclass

from DBDofusUnity.proto_mapper_assembly.interfaces.assembly_access import AccessTraceDocument, MessageAccessSignature
from DBDofusUnity.proto_mapper_assembly.interfaces.capture_sequence_hints import CaptureSequenceHintsConfig
from DBDofusUnity.proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessage
from DBDofusUnity.proto_mapper_assembly.interfaces.enum_mapping import EnumSignatureEntry
from DBDofusUnity.proto_mapper_assembly.interfaces.pinned_pairs import PinnedPairsConfig
from DBDofusUnity.proto_mapper_assembly.interfaces.signature_overrides import SignatureOverrideEntry
from DBDofusUnity.proto_mapper_assembly.runtime.runtime_store import RuntimeDataStore


@dataclass(frozen=True)
class MatchingInputs:
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
    runtime_data_store: RuntimeDataStore
    pinned_pairs_config: PinnedPairsConfig
    capture_sequence_hints_config: CaptureSequenceHintsConfig
