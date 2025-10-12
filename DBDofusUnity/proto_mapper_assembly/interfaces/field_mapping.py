from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Protocol

from DBDofusUnity.proto_mapper_assembly.interfaces.assembly_access import (
    AccessTraceDocument,
    FieldAccessSignatures,
    MessageAccessSignature,
)
from DBDofusUnity.proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessage, DumpCSMessageField, FieldKey
from DBDofusUnity.proto_mapper_assembly.interfaces.enum_mapping import EnumSignatureEntry
from DBDofusUnity.proto_mapper_assembly.interfaces.field_mapping_rejected_infos import (
    FieldMappingRejectedInfos,
)
from DBDofusUnity.proto_mapper_assembly.interfaces.message_pair import MatchPairKey
from DBDofusUnity.proto_mapper_assembly.interfaces.pinned_pairs import PinnedPair
from DBDofusUnity.proto_mapper_assembly.interfaces.signature_overrides import SignatureOverrideEntry
from DBDofusUnity.proto_mapper_assembly.runtime.runtime_store import RuntimeDataStore

type FieldMappingInfos = dict[str, dict[str, float]]
type FieldMappingUnmappedNonObfFields = dict[str, str]


@dataclass(frozen=True)
class FieldMappingContext:
    runtime_data_store: RuntimeDataStore
    score_by_pair: Mapping[MatchPairKey, float]
    signature_overrides_by_non_obf_cls: Mapping[str, SignatureOverrideEntry]
    obf_enum_signatures_by_name: Mapping[str, EnumSignatureEntry]
    non_obf_enum_signatures_by_name: Mapping[str, EnumSignatureEntry]
    obf_access_trace: AccessTraceDocument
    non_obf_access_trace: AccessTraceDocument


@dataclass(frozen=True)
class DiscoveredMessageMatch:
    obf_message_cls: str
    non_obf_message_cls: str
    source_field_obf: str
    source_field_non_obf: str
    confidence: float
    reason: str


@dataclass(frozen=True)
class FieldMappingResult:
    field_mapping: dict[str, str]
    has_validation_failure: bool
    field_mapping_infos: FieldMappingInfos
    discovered_message_matches: tuple[DiscoveredMessageMatch, ...]
    field_mapping_rejected_infos: FieldMappingRejectedInfos
    field_mapping_unmapped_non_obf_fields: FieldMappingUnmappedNonObfFields


class MatchingStoreProtocol(Protocol):
    def supports_pair(self, obf_message_cls: str, non_obf_message_cls: str) -> bool: ...

    def conflicts_with_pair(self, obf_message_cls: str, non_obf_message_cls: str) -> bool: ...


@dataclass(frozen=True)
class MessageSideData:
    """Per-side (obf or non_obf) lookups consumed while mapping fields of a message pair."""

    messages_by_cls: dict[str, DumpCSMessage]
    type_index: dict[str, tuple[DumpCSMessage, ...]]
    fields: tuple[DumpCSMessageField, ...]
    field_signature_by_field_key: dict[FieldKey, FieldAccessSignatures]
    child_cls_by_field_key: dict[FieldKey, str | None]


@dataclass(frozen=True)
class PreparedFieldMappingContext:
    non_obf_signature: MessageAccessSignature
    obf_signature: MessageAccessSignature
    non_obf: MessageSideData
    obf: MessageSideData
    matching_store: MatchingStoreProtocol | None
    field_mapping_context: FieldMappingContext
    pinned_pair: PinnedPair | None = None
