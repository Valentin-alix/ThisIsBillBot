"""A field is a dead candidate only if its message was captured and neither IDA nor runtime shows use."""


import argparse
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from DBDofusUnity.consts import (
    GAME_MAPPINGS_DETAILED_JSON_FILE,
    NON_OBF_PROTO_ACCESSES_FILE,
    NON_OBF_PROTOCOL_GAME_DUMP_CS_FILE,
    NON_OBFUSCATED_DATA_DIR,
    OBF_PROTO_ACCESSES_FILE,
    OBF_PROTOCOL_GAME_DUMP_CS_FILE,
    OBFUSCATED_DATA_DIR,
    PROTOS_ROOT,
)
from DBDofusUnity.proto_mapper_assembly.controllers.game_mappings import load_game_mappings_document
from DBDofusUnity.proto_mapper_assembly.helpers.non_obf_names import build_filtered_message_namespace
from DBDofusUnity.proto_mapper_assembly.interfaces.assembly_access import (
    FunctionAccessInfo,
    ProtoAccessesInfo,
    TypeInfoAccessEntry,
    is_field_access_entry,
)
from DBDofusUnity.proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessage, DumpCSMessageField
from DBDofusUnity.proto_mapper_assembly.interfaces.enum_mapping import EnumSignatureEntry
from DBDofusUnity.proto_mapper_assembly.interfaces.field_category import FieldCategoryEnum
from DBDofusUnity.proto_mapper_assembly.interfaces.game_mappings import GameMappingEntry, GameMappingsDocument
from DBDofusUnity.proto_mapper_assembly.interfaces.il2cpp_json import Il2CppJson
from DBDofusUnity.proto_mapper_assembly.parsers.csharp_signature_utils import (
    CORE_METHOD_DECLARATION_RE as _CORE_METHOD_DECLARATION_RE,
)
from DBDofusUnity.proto_mapper_assembly.parsers.csharp_signature_utils import (
    canonicalize_csharp_method_declaration as _canonicalize_csharp_method_declaration,
)
from DBDofusUnity.proto_mapper_assembly.parsers.dump_cs_parser import parse_messages
from DBDofusUnity.proto_mapper_assembly.parsers.proto_accesses_parser import (
    parse_access_trace_document,
    parse_proto_accesses,
)
from DBDofusUnity.proto_mapper_assembly.parsers.protobuf_dump_cs import build_dump_cs_messages_from_pb2
from DBDofusUnity.proto_mapper_assembly.runtime.runtime_field_validation import collect_runtime_alive_field_names
from DBDofusUnity.proto_mapper_assembly.runtime.runtime_store import RuntimeDataStore
from DBDofusUnity.proto_mapper_assembly.scripts.ida_tracer_lib.lookups.type_lookup import build_long_name_by_unique_alias
from DBDofusUnity.proto_mapper_assembly.scripts.ida_tracer_lib.signatures.parser import (
    extract_proto_parameter_seeds,
    select_signature_for_proto_tracking,
)

type ZeroAccessBucket = Literal[
    "partial_field_access",
    "seeded_core_no_fields",
    "typeinfo_only",
    "no_core_evidence",
]
type ZeroAccessCause = Literal[
    "partial_missing_offsets",
    "synthetic_oneof_case",
    "seeded_proto_param_unused",
    "typeinfo_wrapper_constructor",
    "typeinfo_dispatch_return_only",
    "no_core_evidence",
]

_STUB_METHOD_SIZE_THRESHOLD = 0x10


@dataclass(frozen=True, slots=True)
class CoreMethodEvidence:
    address: int
    group: str
    signature: str
    size: int | None = None

    @property
    def is_stub(self) -> bool:
        return self.size is not None and self.size <= _STUB_METHOD_SIZE_THRESHOLD


@dataclass(frozen=True, slots=True)
class ZeroAccessExplanation:
    cls: str
    fields: list[DumpCSMessageField]
    bucket: ZeroAccessBucket
    likely_cause: ZeroAccessCause
    accessed_offsets: frozenset[int]
    seeded_methods: list[CoreMethodEvidence]
    typeinfo_only_functions: list[str]


@dataclass(frozen=True, slots=True)
class _CoreMethodMetadata:
    signature: str
    size: int


def main() -> None:
    args = _build_argument_parser().parse_args()

    if args.unknown_fields:
        print(format_unknown_field_audit(build_unknown_field_audit()))
        return

    if args.obf:
        dump_cs_path = str(OBF_PROTOCOL_GAME_DUMP_CS_FILE)
        proto_accesses_path = str(OBF_PROTO_ACCESSES_FILE)
        base_dir = OBFUSCATED_DATA_DIR
        label = "obf"
    else:
        dump_cs_path = str(NON_OBF_PROTOCOL_GAME_DUMP_CS_FILE)
        proto_accesses_path = str(NON_OBF_PROTO_ACCESSES_FILE)
        base_dir = NON_OBFUSCATED_DATA_DIR
        label = "non-obf"

    print(f"Loading {label} data...")
    messages = parse_messages(dump_cs_path)
    access_trace = parse_access_trace_document(proto_accesses_path)
    proto_accesses = parse_proto_accesses(proto_accesses_path)
    enum_signatures = access_trace.enum_signatures_by_name

    zero_access = find_zero_access_fields(messages, proto_accesses, enum_signatures)
    if args.explain:
        core_methods_by_class = build_core_proto_seed_evidence(base_dir, messages)
        explanations = collect_zero_access_explanations(
            messages,
            proto_accesses,
            enum_signatures,
            core_methods_by_class,
        )
        print(format_explain_report(explanations))
    else:
        print(format_report(zero_access))


def _build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Report proto message fields with 0 access detected in proto_accesses."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--obf", action="store_true", help="Check obfuscated build")
    group.add_argument("--non-obf", action="store_true", dest="non_obf", help="Check non-obfuscated build")
    group.add_argument(
        "--unknown-fields",
        action="store_true",
        dest="unknown_fields",
        help="Audit declared unknown_* fields against the obfuscated trace and the runtime captures.",
    )
    parser.add_argument(
        "--explain",
        action="store_true",
        help="Group zero-access fields by tracer evidence bucket. Ignored with --unknown-fields.",
    )
    return parser


def find_zero_access_fields(
    messages: list[DumpCSMessage],
    proto_accesses: ProtoAccessesInfo,
    enum_signatures: dict[str, EnumSignatureEntry],
) -> list[tuple[str, DumpCSMessageField]]:
    property_offset_by_cls = _build_property_offset_by_cls(messages)
    proto_accessed = _collect_proto_accessed_offsets(proto_accesses, property_offset_by_cls)
    enum_accessed = _collect_enum_accessed_offsets(messages, enum_signatures)

    result: list[tuple[str, DumpCSMessageField]] = []
    for message in messages:
        cls = message.composed_name
        accessed_offsets = proto_accessed.get(cls, set()) | enum_accessed.get(cls, set())
        for field in message.fields:
            if not field.is_declared_proto_shape_field:
                continue
            if field.memory_offset not in accessed_offsets:
                result.append((cls, field))

    return result


def _build_property_offset_by_cls(messages: list[DumpCSMessage]) -> dict[str, dict[str, int]]:
    result: dict[str, dict[str, int]] = defaultdict(dict)
    for message in messages:
        for field in message.fields:
            if field.property_name is None:
                continue
            result[message.composed_name][field.property_name] = field.memory_offset
    return result


def _collect_proto_accessed_offsets(
    proto_accesses: ProtoAccessesInfo,
    property_offset_by_cls: dict[str, dict[str, int]],
) -> dict[str, set[int]]:
    accessed: dict[str, set[int]] = defaultdict(set)
    for func_info in proto_accesses.root.values():
        for access in func_info.access_infos:
            if not is_field_access_entry(access):
                continue
            if access.field_offset is not None:
                accessed[access.cls].add(access.field_offset)
                continue
            if access.property_name is None:
                continue
            offset = property_offset_by_cls.get(access.cls, {}).get(access.property_name)
            if offset is not None:
                accessed[access.cls].add(offset)

    return accessed


def _collect_enum_accessed_offsets(
    messages: list[DumpCSMessage],
    enum_signatures: dict[str, EnumSignatureEntry],
) -> dict[str, set[int]]:
    accessed: dict[str, set[int]] = defaultdict(set)
    for message in messages:
        for field in message.fields:
            if field.category != FieldCategoryEnum.ENUM or not field.enum_value_type:
                continue

            entry = enum_signatures.get(field.enum_value_type)
            if entry is None:
                continue

            if any(pattern.field_offset == field.memory_offset for pattern in entry.switch_patterns):
                accessed[message.composed_name].add(field.memory_offset)

    return accessed


def format_report(zero_access_fields: list[tuple[str, DumpCSMessageField]]) -> str:
    by_message: dict[str, list[DumpCSMessageField]] = defaultdict(list)
    for cls, field in zero_access_fields:
        by_message[cls].append(field)

    lines: list[str] = []
    for cls in sorted(by_message):
        fields = by_message[cls]
        lines.append(f"\n{cls} ({len(fields)} zero-access field(s)):")
        lines.extend(
            f"  - {field.clean_field_name}  offset={field.memory_offset}  type={field.clr_type}"
            for field in sorted(fields, key=lambda field: field.memory_offset)
        )

    total_fields = len(zero_access_fields)
    total_msgs = len(by_message)
    msg_label = "message" if total_msgs == 1 else "messages"
    lines.append(f"\n=== {total_fields} zero-access fields across {total_msgs} {msg_label} ===")

    return "\n".join(lines)


def build_core_proto_seed_evidence(
    base_dir: Path,
    messages: list[DumpCSMessage],
) -> dict[str, list[CoreMethodEvidence]]:
    il2cpp_path = base_dir / "il2cpp.json"
    if not il2cpp_path.exists():
        return {}

    method_metadata_by_address = _build_core_method_metadata_lookup(base_dir)
    message_type_lookup = build_long_name_by_unique_alias(messages)
    il2cpp = Il2CppJson.model_validate_json(il2cpp_path.read_text(encoding="utf-8"))

    result: dict[str, list[CoreMethodEvidence]] = defaultdict(list)
    for method in il2cpp.address_map.method_definitions:
        if not method.group.startswith("Core.dll"):
            continue

        method_address = int(method.virtual_address, 16)
        method_metadata = method_metadata_by_address.get(method_address)
        fallback_signature = method_metadata.signature if method_metadata is not None else None
        selected_signature = select_signature_for_proto_tracking(
            method,
            message_type_lookup,
            fallback_signature=fallback_signature,
        )

        for _, _, cls in extract_proto_parameter_seeds(
            method,
            message_type_lookup,
            preferred_signature=selected_signature,
        ):
            result[cls].append(
                CoreMethodEvidence(
                    address=method_address,
                    group=method.group,
                    signature=selected_signature or method.name,
                    size=method_metadata.size if method_metadata is not None else None,
                )
            )

    return dict(result)


def _build_core_method_metadata_lookup(base_dir: Path) -> dict[int, _CoreMethodMetadata]:
    core_cs_path = base_dir / "cs" / "Core.cs"
    if not core_cs_path.exists():
        return {}

    result: dict[int, _CoreMethodMetadata] = {}
    for raw_line in core_cs_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        matched = _CORE_METHOD_DECLARATION_RE.match(raw_line)
        if matched is None:
            continue

        signature = _canonicalize_csharp_method_declaration(matched.group("declaration"))
        if signature is None:
            continue

        start_address = int(matched.group("start"), 16)
        end_address = int(matched.group("end"), 16)
        result[start_address] = _CoreMethodMetadata(
            signature=signature,
            size=end_address - start_address,
        )

    return result


def collect_zero_access_explanations(
    messages: list[DumpCSMessage],
    proto_accesses: ProtoAccessesInfo,
    enum_signatures: dict[str, EnumSignatureEntry],
    core_methods_by_class: Mapping[str, list[CoreMethodEvidence]] | None = None,
) -> list[ZeroAccessExplanation]:
    zero_access_fields = find_zero_access_fields(messages, proto_accesses, enum_signatures)

    fields_by_class: dict[str, list[DumpCSMessageField]] = defaultdict(list)
    for cls, field in zero_access_fields:
        fields_by_class[cls].append(field)

    property_offset_by_cls = _build_property_offset_by_cls(messages)
    proto_accessed_offsets = _collect_proto_accessed_offsets(proto_accesses, property_offset_by_cls)
    enum_accessed_offsets = _collect_enum_accessed_offsets(messages, enum_signatures)
    typeinfo_only_functions = _collect_typeinfo_only_functions(proto_accesses)
    function_infos_by_key = proto_accesses.root
    resolved_core_methods_by_class = core_methods_by_class or {}

    explanations: list[ZeroAccessExplanation] = []
    for cls in sorted(fields_by_class):
        accessed_offsets = frozenset(
            proto_accessed_offsets.get(cls, set()) | enum_accessed_offsets.get(cls, set())
        )
        seeded_methods = resolved_core_methods_by_class.get(cls, [])
        non_stub_seeded_methods = [method for method in seeded_methods if not method.is_stub]
        bucket = _classify_zero_access_bucket(
            accessed_offsets,
            non_stub_seeded_methods,
            typeinfo_only_functions.get(cls, []),
        )
        likely_cause = _classify_zero_access_cause(
            bucket,
            fields_by_class[cls],
            accessed_offsets,
            non_stub_seeded_methods,
            typeinfo_only_functions.get(cls, []),
            function_infos_by_key,
        )
        explanations.append(
            ZeroAccessExplanation(
                cls=cls,
                fields=sorted(fields_by_class[cls], key=lambda field: field.memory_offset),
                bucket=bucket,
                likely_cause=likely_cause,
                accessed_offsets=accessed_offsets,
                seeded_methods=list(seeded_methods),
                typeinfo_only_functions=typeinfo_only_functions.get(cls, []),
            )
        )

    return explanations


def _collect_typeinfo_only_functions(proto_accesses: ProtoAccessesInfo) -> dict[str, list[str]]:
    result: dict[str, list[str]] = defaultdict(list)
    for function_key, func_info in proto_accesses.root.items():
        classes = {access.cls for access in func_info.access_infos}
        for cls in classes:
            class_accesses = [access for access in func_info.access_infos if access.cls == cls]
            if any(is_field_access_entry(access) for access in class_accesses):
                continue
            result[cls].append(function_key)

    return result


def _classify_zero_access_bucket(
    accessed_offsets: frozenset[int],
    non_stub_seeded_methods: list[CoreMethodEvidence],
    typeinfo_only_functions: list[str],
) -> ZeroAccessBucket:
    if accessed_offsets:
        return "partial_field_access"
    if non_stub_seeded_methods:
        return "seeded_core_no_fields"
    if typeinfo_only_functions:
        return "typeinfo_only"
    return "no_core_evidence"


def _classify_zero_access_cause(
    bucket: ZeroAccessBucket,
    fields: list[DumpCSMessageField],
    accessed_offsets: frozenset[int],
    non_stub_seeded_methods: list[CoreMethodEvidence],
    typeinfo_only_functions: list[str],
    function_infos_by_key: Mapping[str, FunctionAccessInfo],
) -> ZeroAccessCause:
    if any(field.is_synthetic_oneof_variant for field in fields):
        return "synthetic_oneof_case"
    if bucket == "partial_field_access" or accessed_offsets:
        return "partial_missing_offsets"
    if bucket == "seeded_core_no_fields":
        return "seeded_proto_param_unused"
    if _has_typeinfo_dispatch_return_only(typeinfo_only_functions, function_infos_by_key):
        return "typeinfo_dispatch_return_only"
    if typeinfo_only_functions:
        return "typeinfo_wrapper_constructor"
    if non_stub_seeded_methods:
        return "seeded_proto_param_unused"
    return "no_core_evidence"


def _has_typeinfo_dispatch_return_only(
    typeinfo_only_functions: list[str],
    function_infos_by_key: Mapping[str, FunctionAccessInfo],
) -> bool:
    for function_key in typeinfo_only_functions:
        func_info = function_infos_by_key.get(function_key)
        if func_info is None:
            continue

        typeinfo_classes = {
            access.cls for access in func_info.access_infos if isinstance(access, TypeInfoAccessEntry)
        }
        field_classes = {access.cls for access in func_info.access_infos if is_field_access_entry(access)}
        if field_classes and len(typeinfo_classes) > len(field_classes):
            return True

    return False


def format_explain_report(explanations: list[ZeroAccessExplanation]) -> str:
    by_bucket: dict[ZeroAccessBucket, list[ZeroAccessExplanation]] = defaultdict(list)
    by_cause: dict[ZeroAccessCause, list[ZeroAccessExplanation]] = defaultdict(list)
    for explanation in explanations:
        by_bucket[explanation.bucket].append(explanation)
        by_cause[explanation.likely_cause].append(explanation)

    bucket_order: tuple[ZeroAccessBucket, ...] = (
        "partial_field_access",
        "seeded_core_no_fields",
        "typeinfo_only",
        "no_core_evidence",
    )
    cause_order: tuple[ZeroAccessCause, ...] = (
        "partial_missing_offsets",
        "synthetic_oneof_case",
        "seeded_proto_param_unused",
        "typeinfo_dispatch_return_only",
        "typeinfo_wrapper_constructor",
        "no_core_evidence",
    )

    lines: list[str] = ["[likely_cause_summary]"]
    for cause in cause_order:
        cause_entries = by_cause.get(cause, [])
        field_count = sum(len(entry.fields) for entry in cause_entries)
        lines.append(f"  {cause}: {field_count} field(s) across {len(cause_entries)} message(s)")

    for bucket in bucket_order:
        bucket_entries = by_bucket.get(bucket, [])
        field_count = sum(len(entry.fields) for entry in bucket_entries)
        lines.append(f"\n[{bucket}] {field_count} field(s) across {len(bucket_entries)} message(s)")
        for entry in bucket_entries:
            field_summary = ", ".join(
                f"{field.clean_field_name}@{field.memory_offset}" for field in entry.fields
            )
            lines.append(f"  - {entry.cls}: {field_summary}")
            lines.append(f"    likely_cause: {entry.likely_cause}")

            if entry.accessed_offsets:
                offsets = ", ".join(str(offset) for offset in sorted(entry.accessed_offsets))
                lines.append(f"    accessed_offsets: {offsets}")

            non_stub_methods = [method for method in entry.seeded_methods if not method.is_stub]
            stub_methods = [method for method in entry.seeded_methods if method.is_stub]

            if non_stub_methods:
                method_summary = "; ".join(
                    f"{method.group}@0x{method.address:X}:{method.signature}"
                    for method in non_stub_methods[:3]
                )
                lines.append(f"    seeded_core: {method_summary}")

            if stub_methods:
                lines.append(f"    ignored_stub_seeded_core: {len(stub_methods)}")

            if entry.typeinfo_only_functions:
                typeinfo_summary = "; ".join(entry.typeinfo_only_functions[:3])
                lines.append(f"    typeinfo_only: {typeinfo_summary}")

    total_fields = sum(len(entry.fields) for entry in explanations)
    lines.append(f"\n=== explained {total_fields} zero-access fields across {len(explanations)} messages ===")

    return "\n".join(lines)


type UnknownFieldAuditStatus = Literal["active", "dead_candidate", "inconclusive"]
type UnknownFieldAuditReason = Literal[
    "ida_access",
    "runtime_non_default",
    "no_evidence",
    "no_runtime_capture",
    "no_root_mapping",
    "no_unique_field_mapping",
    "missing_obf_message",
    "missing_obf_field",
]


@dataclass(frozen=True, slots=True)
class UnknownFieldAuditRecord:
    non_obf_message: str
    non_obf_field: str
    status: UnknownFieldAuditStatus
    reason: UnknownFieldAuditReason
    obf_message: str | None = None
    obf_field: str | None = None
    capture_count: int | None = None
    has_ida_access: bool | None = None
    has_runtime_non_default_value: bool | None = None


def audit_unknown_fields(
    *,
    non_obf_messages_by_cls: Mapping[str, DumpCSMessage],
    obf_messages_by_cls: Mapping[str, DumpCSMessage],
    game_mappings: GameMappingsDocument,
    accessed_offsets_by_obf_message: Mapping[str, set[int]],
    runtime_instances_by_obf_message: Mapping[str, Sequence[Mapping[str, object]]],
) -> list[UnknownFieldAuditRecord]:
    records: list[UnknownFieldAuditRecord] = []
    for non_obf_message in non_obf_messages_by_cls.values():
        non_obf_namespace = build_filtered_message_namespace(
            is_obf=False,
            message=non_obf_message,
            messages_by_cls=non_obf_messages_by_cls,
        )
        mapping = game_mappings.root.get(non_obf_namespace)
        for non_obf_field in non_obf_message.fields:
            if not non_obf_field.is_declared_proto_shape_field:
                continue
            if not non_obf_field.clean_field_name.startswith("unknown_"):
                continue
            records.append(
                _audit_unknown_field(
                    non_obf_namespace=non_obf_namespace,
                    non_obf_field_name=non_obf_field.clean_field_name,
                    mapping=mapping,
                    obf_messages_by_cls=obf_messages_by_cls,
                    accessed_offsets_by_obf_message=accessed_offsets_by_obf_message,
                    runtime_instances_by_obf_message=runtime_instances_by_obf_message,
                )
            )
    return sorted(records, key=lambda record: (record.status, record.non_obf_message, record.non_obf_field))


def _audit_unknown_field(
    *,
    non_obf_namespace: str,
    non_obf_field_name: str,
    mapping: GameMappingEntry | None,
    obf_messages_by_cls: Mapping[str, DumpCSMessage],
    accessed_offsets_by_obf_message: Mapping[str, set[int]],
    runtime_instances_by_obf_message: Mapping[str, Sequence[Mapping[str, object]]],
) -> UnknownFieldAuditRecord:
    if mapping is None:
        return UnknownFieldAuditRecord(
            non_obf_message=non_obf_namespace,
            non_obf_field=non_obf_field_name,
            status="inconclusive",
            reason="no_root_mapping",
        )

    obf_field_names = [
        obf_field_name
        for obf_field_name, mapped_non_obf_field_name in mapping.field_mapping.items()
        if mapped_non_obf_field_name == non_obf_field_name
    ]
    if len(obf_field_names) != 1:
        return UnknownFieldAuditRecord(
            non_obf_message=non_obf_namespace,
            non_obf_field=non_obf_field_name,
            status="inconclusive",
            reason="no_unique_field_mapping",
            obf_message=mapping.full_obf_msg_namespace,
        )

    obf_message = obf_messages_by_cls.get(mapping.full_obf_msg_namespace)
    if obf_message is None:
        return UnknownFieldAuditRecord(
            non_obf_message=non_obf_namespace,
            non_obf_field=non_obf_field_name,
            status="inconclusive",
            reason="missing_obf_message",
            obf_message=mapping.full_obf_msg_namespace,
            obf_field=obf_field_names[0],
        )

    obf_field_name = obf_field_names[0]
    obf_field = next(
        (field for field in obf_message.fields if field.clean_field_name == obf_field_name),
        None,
    )
    if obf_field is None:
        return UnknownFieldAuditRecord(
            non_obf_message=non_obf_namespace,
            non_obf_field=non_obf_field_name,
            status="inconclusive",
            reason="missing_obf_field",
            obf_message=obf_message.composed_name,
            obf_field=obf_field_name,
        )

    runtime_instances = runtime_instances_by_obf_message.get(obf_message.composed_name, ())
    has_runtime_non_default_value = obf_field_name in collect_runtime_alive_field_names(runtime_instances)
    has_ida_access = obf_field.memory_offset in accessed_offsets_by_obf_message.get(
        obf_message.composed_name, set()
    )
    if has_ida_access:
        return UnknownFieldAuditRecord(
            non_obf_message=non_obf_namespace,
            non_obf_field=non_obf_field_name,
            status="active",
            reason="ida_access",
            obf_message=obf_message.composed_name,
            obf_field=obf_field_name,
            capture_count=len(runtime_instances),
            has_ida_access=True,
            has_runtime_non_default_value=has_runtime_non_default_value,
        )
    if has_runtime_non_default_value:
        return UnknownFieldAuditRecord(
            non_obf_message=non_obf_namespace,
            non_obf_field=non_obf_field_name,
            status="active",
            reason="runtime_non_default",
            obf_message=obf_message.composed_name,
            obf_field=obf_field_name,
            capture_count=len(runtime_instances),
            has_ida_access=False,
            has_runtime_non_default_value=True,
        )
    if not runtime_instances:
        return UnknownFieldAuditRecord(
            non_obf_message=non_obf_namespace,
            non_obf_field=non_obf_field_name,
            status="inconclusive",
            reason="no_runtime_capture",
            obf_message=obf_message.composed_name,
            obf_field=obf_field_name,
            capture_count=0,
            has_ida_access=False,
            has_runtime_non_default_value=False,
        )
    return UnknownFieldAuditRecord(
        non_obf_message=non_obf_namespace,
        non_obf_field=non_obf_field_name,
        status="dead_candidate",
        reason="no_evidence",
        obf_message=obf_message.composed_name,
        obf_field=obf_field_name,
        capture_count=len(runtime_instances),
        has_ida_access=False,
        has_runtime_non_default_value=False,
    )


def format_unknown_field_audit(records: Sequence[UnknownFieldAuditRecord]) -> str:
    counts_by_status = Counter(record.status for record in records)
    counts_by_reason = Counter(record.reason for record in records)
    lines = [
        "=== Unknown field audit ===",
        f"Total declared unknown fields: {len(records)}",
        *(f"{status}: {counts_by_status[status]}" for status in sorted(counts_by_status)),
        "",
        "Reasons:",
        *(f"{reason}: {counts_by_reason[reason]}" for reason in sorted(counts_by_reason)),
    ]
    by_status: dict[UnknownFieldAuditStatus, list[UnknownFieldAuditRecord]] = defaultdict(list)
    for record in records:
        by_status[record.status].append(record)
    for status in ("dead_candidate", "inconclusive", "active"):
        lines.append(f"\n[{status}]")
        for record in by_status[status]:
            lines.append(_format_record(record))
    return "\n".join(lines)


def _format_record(record: UnknownFieldAuditRecord) -> str:
    target = record.non_obf_message + "." + record.non_obf_field
    source = "unresolved"
    if record.obf_message is not None and record.obf_field is not None:
        source = record.obf_message + "." + record.obf_field
    evidence = f"captures={record.capture_count} ida={record.has_ida_access} runtime={record.has_runtime_non_default_value}"
    return f"- {target} <- {source} [{record.reason}; {evidence}]"


def build_unknown_field_audit() -> list[UnknownFieldAuditRecord]:
    non_obf_messages_by_cls = build_dump_cs_messages_from_pb2(PROTOS_ROOT / "non_obf")
    obf_messages = parse_messages(str(OBF_PROTOCOL_GAME_DUMP_CS_FILE))
    obf_messages_by_cls = {message.composed_name: message for message in obf_messages}
    access_trace = parse_access_trace_document(str(OBF_PROTO_ACCESSES_FILE))
    proto_accesses = parse_proto_accesses(str(OBF_PROTO_ACCESSES_FILE))
    property_offsets = _build_property_offset_by_cls(obf_messages)
    proto_accessed_offsets = _collect_proto_accessed_offsets(proto_accesses, property_offsets)
    enum_accessed_offsets = _collect_enum_accessed_offsets(
        obf_messages,
        access_trace.enum_signatures_by_name,
    )
    accessed_offsets_by_obf_message = {
        obf_message_name: proto_accessed_offsets.get(obf_message_name, set())
        | enum_accessed_offsets.get(obf_message_name, set())
        for obf_message_name in obf_messages_by_cls
    }
    runtime_store = RuntimeDataStore()
    runtime_instances_by_obf_message = {
        obf_message_name: runtime_store.get_normalized_content_for_obf_message(
            message=obf_message,
            obf_messages_by_cls=obf_messages_by_cls,
        )
        for obf_message_name, obf_message in obf_messages_by_cls.items()
    }
    return audit_unknown_fields(
        non_obf_messages_by_cls=non_obf_messages_by_cls,
        obf_messages_by_cls=obf_messages_by_cls,
        game_mappings=load_game_mappings_document(GAME_MAPPINGS_DETAILED_JSON_FILE),
        accessed_offsets_by_obf_message=accessed_offsets_by_obf_message,
        runtime_instances_by_obf_message=runtime_instances_by_obf_message,
    )


if __name__ == "__main__":
    main()
