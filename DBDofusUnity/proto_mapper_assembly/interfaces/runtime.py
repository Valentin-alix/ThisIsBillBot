from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel

from DBDofusUnity.proto_mapper_assembly.interfaces.assembly_access import MessageAccessSignature
from DBDofusUnity.proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessage, DumpCSMessageField, FieldKey
from DBDofusUnity.proto_mapper_assembly.interfaces.field_mapping import FieldMappingResult

type MappingFailureOrigin = Literal["child"]
type RuntimeTraceKind = Literal["failure"]


@dataclass(frozen=True)
class MessageRuntimeMetadata:
    live_runtime_fields_by_name: dict[str, DumpCSMessageField]
    child_message_cls_by_field_key: dict[FieldKey, str | None]


@dataclass(frozen=True)
class RuntimeValidationCandidate:
    obf_msg_sig: MessageAccessSignature
    non_obf_msg_sig: MessageAccessSignature
    obf_index: int
    non_obf_index: int
    field_mapping_result: FieldMappingResult


@dataclass(frozen=True)
class RuntimeRemappingResult:
    instances_by_type: dict[str, list[dict[str, object]]]
    mapping_failure: str | None = None
    mapping_failure_origin: MappingFailureOrigin | None = None


@dataclass(frozen=True)
class RuntimeRemappingTraceEvent:
    kind: RuntimeTraceKind
    path: tuple[str, ...]
    message: str
    mapping_failure_origin: MappingFailureOrigin | None = None


@dataclass(frozen=True)
class RemapOutcome:
    value: object
    mapping_failure: str | None = None
    mapping_failure_origin: MappingFailureOrigin | None = None


@dataclass(frozen=True)
class ChildMappingResolution:
    status: Literal["resolved", "unresolved"]
    child_candidate: RuntimeValidationCandidate | None = None


@dataclass(frozen=True)
class RuntimeRemappingContext:
    candidates_by_non_obf: dict[str, dict[str, RuntimeValidationCandidate]]
    obf_messages_by_cls: dict[str, DumpCSMessage]
    non_obf_messages_by_cls: dict[str, DumpCSMessage]
    get_obf_metadata: Callable[[DumpCSMessage], MessageRuntimeMetadata]
    get_non_obf_metadata: Callable[[DumpCSMessage], MessageRuntimeMetadata]


class FieldValidatorRuntimeMetadata(BaseModel):
    did_validation_run: bool
    did_validation_failure: bool
    failed_value: object | None = None
