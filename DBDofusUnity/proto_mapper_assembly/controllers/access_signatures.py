from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence

from proto_mapper_assembly.controllers.message_fields import (
    build_message_field_resolution_lookup,
    resolve_field_by_access_entry,
)
from proto_mapper_assembly.interfaces.assembly_access import (
    AccessAtomSignature,
    AccessEntry,
    AccessTraceDocument,
    FieldAccessSignatures,
    FunctionAccessInfo,
    FunctionAccessSignature,
    MessageAccessSignature,
    ProtoAccessesInfo,
    is_field_access_entry,
)
from proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessage, FieldKey
from proto_mapper_assembly.interfaces.enum_mapping import EnumSignatureEntry
from proto_mapper_assembly.interfaces.field_category import FieldCategoryEnum
from proto_mapper_assembly.interfaces.message_field_resolution_lookup import MessageFieldResolutionLookup
from proto_mapper_assembly.parsers.csharp_signature_utils import get_normalized_short_type_name
from proto_mapper_assembly.parsers.proto_accesses_parser import parse_access_trace_document


def load_message_access_signatures_from_messages(
    proto_accesses_path: str,
    messages: Sequence[DumpCSMessage],
) -> dict[str, MessageAccessSignature]:
    access_trace = parse_access_trace_document(proto_accesses_path)
    return build_message_access_signatures_from_trace(
        access_trace=access_trace,
        messages=messages,
    )


def build_message_access_signatures_from_trace(
    *,
    access_trace: AccessTraceDocument,
    messages: Sequence[DumpCSMessage],
) -> dict[str, MessageAccessSignature]:
    return build_message_access_signatures_by_cls(
        proto_accesses=access_trace.to_proto_accesses(),
        dump_cs_msg_by_message_cls={message.composed_name: message for message in messages},
        field_resolution_by_message_cls=build_message_field_resolution_lookup(messages),
        enum_signatures=access_trace.enum_signatures_by_name,
    )


def build_message_access_signatures_by_cls(
    proto_accesses: ProtoAccessesInfo,
    dump_cs_msg_by_message_cls: dict[str, DumpCSMessage],
    field_resolution_by_message_cls: dict[str, MessageFieldResolutionLookup],
    enum_signatures: dict[str, EnumSignatureEntry],
) -> dict[str, MessageAccessSignature]:
    function_signatures_by_cls = _collect_function_signatures_by_message_cls(
        proto_accesses, field_resolution_by_message_cls
    )
    field_signatures_by_cls = _collect_field_signatures_by_message_cls(
        proto_accesses, field_resolution_by_message_cls
    )
    if enum_signatures:
        enum_field_signatures_by_cls = _collect_field_signatures_from_enum_accesses(
            field_resolution_by_message_cls, enum_signatures
        )
        for message_cls, enum_field_signatures in enum_field_signatures_by_cls.items():
            for field_key, access_atoms in enum_field_signatures.items():
                field_signatures_by_cls[message_cls].setdefault(field_key, access_atoms)

    message_signatures: dict[str, MessageAccessSignature] = {}

    for message_cls in dump_cs_msg_by_message_cls:
        message_signatures[message_cls] = _build_message_signature(
            message_cls=message_cls,
            function_signatures=[],
            dump_cs_msg_by_message_cls=dump_cs_msg_by_message_cls,
            field_signatures_by_key=field_signatures_by_cls.get(message_cls, {}),
            field_resolution=field_resolution_by_message_cls[message_cls],
        )

    for message_cls in sorted(function_signatures_by_cls):
        dump_cs_msg = dump_cs_msg_by_message_cls.get(message_cls)
        if dump_cs_msg is None:
            message = f"Missing dump.cs file descriptor lookup for runtime message class: {message_cls}"
            raise ValueError(message)
        field_resolution = field_resolution_by_message_cls.get(message_cls)
        if field_resolution is None:
            message = f"Missing dump.cs field resolution lookup for runtime message class: {message_cls}"
            raise ValueError(message)
        message_signatures[message_cls] = _build_message_signature(
            message_cls=message_cls,
            function_signatures=function_signatures_by_cls.get(message_cls, []),
            dump_cs_msg_by_message_cls=dump_cs_msg_by_message_cls,
            field_signatures_by_key=field_signatures_by_cls.get(message_cls, {}),
            field_resolution=field_resolution,
        )

    return message_signatures


def get_message_clss_from_parameters(
    parameters: Sequence[str],
    short_name_to_cls: dict[str, str],
) -> set[str]:
    message_clss: set[str] = set()
    for parameter in parameters:
        message_cls = short_name_to_cls.get(get_normalized_short_type_name(parameter))
        if message_cls is not None:
            message_clss.add(message_cls)
    return message_clss


def _collect_function_signatures_by_message_cls(
    proto_accesses: ProtoAccessesInfo,
    field_resolution_by_message_cls: dict[str, MessageFieldResolutionLookup],
) -> dict[str, list[FunctionAccessSignature]]:
    function_signatures_by_cls: dict[str, list[FunctionAccessSignature]] = defaultdict(list)
    short_name_to_cls = _build_short_name_to_cls(field_resolution_by_message_cls)
    for function_info in proto_accesses.root.values():
        function_signatures = _build_function_access_signatures_by_cls(
            function_info, field_resolution_by_message_cls, short_name_to_cls
        )
        for message_cls, function_signature in function_signatures.items():
            function_signatures_by_cls[message_cls].append(function_signature)
    return function_signatures_by_cls


def _collect_field_signatures_by_message_cls(
    proto_accesses: ProtoAccessesInfo,
    field_resolution_by_message_cls: dict[str, MessageFieldResolutionLookup],
) -> dict[str, dict[FieldKey, list[AccessAtomSignature]]]:
    field_signatures_by_cls: dict[str, dict[FieldKey, list[AccessAtomSignature]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for function_info in proto_accesses.root.values():
        for access in function_info.access_infos:
            if not is_field_access_entry(access):
                continue
            resolved_field = resolve_field_by_access_entry(access, field_resolution_by_message_cls)
            if not resolved_field.is_declared_proto_shape_field:
                continue
            access_atoms = field_signatures_by_cls[access.cls][resolved_field.field_key]
            if access.field_offset is not None:
                access_atoms.append(_build_access_atom_signature(access, field_resolution_by_message_cls))
    return field_signatures_by_cls


def _collect_field_signatures_from_enum_accesses(
    field_resolution_by_message_cls: dict[str, MessageFieldResolutionLookup],
    enum_signatures: dict[str, EnumSignatureEntry],
) -> dict[str, dict[FieldKey, list[AccessAtomSignature]]]:
    field_signatures_by_cls: dict[str, dict[FieldKey, list[AccessAtomSignature]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for message_cls, field_resolution in field_resolution_by_message_cls.items():
        for field in field_resolution.declared_proto_fields:
            if field.category != FieldCategoryEnum.ENUM:
                continue
            enum_name = field.enum_value_type
            assert enum_name
            if enum_name not in enum_signatures:
                continue
            entry = enum_signatures[enum_name]
            if any(pattern.field_offset == field.memory_offset for pattern in entry.switch_patterns):
                field_signatures_by_cls[message_cls][field.field_key]
    return field_signatures_by_cls


def _build_message_signature(
    message_cls: str,
    function_signatures: list[FunctionAccessSignature],
    dump_cs_msg_by_message_cls: dict[str, DumpCSMessage],
    field_signatures_by_key: dict[FieldKey, list[AccessAtomSignature]],
    field_resolution: MessageFieldResolutionLookup,
) -> MessageAccessSignature:
    dump_cs_msg = dump_cs_msg_by_message_cls[message_cls]

    field_signatures: list[FieldAccessSignatures] = []
    for field_key, accesses in sorted(field_signatures_by_key.items(), key=lambda item: item[0]):
        field = field_resolution.declared_field_by_key[field_key]
        field_signatures.append(
            FieldAccessSignatures(
                field_key=field_key,
                field_type_shape=field.field_type_shape,
                accesses=accesses,
            )
        )

    return MessageAccessSignature(
        message_cls=message_cls,
        dump_cs_msg=dump_cs_msg,
        file_descriptor=dump_cs_msg.file_descriptor,
        function_signatures=function_signatures,
        field_signatures=field_signatures,
    )


def _build_function_access_signatures_by_cls(
    function_info: FunctionAccessInfo,
    field_resolution_by_message_cls: dict[str, MessageFieldResolutionLookup],
    short_name_to_cls: dict[str, str],
) -> dict[str, FunctionAccessSignature]:
    message_clss_from_parameters = get_message_clss_from_parameters(
        function_info.parameters, short_name_to_cls
    )
    all_message_clss = set(function_info.accesses_by_cls) | message_clss_from_parameters

    return {
        message_cls: _build_function_signature_for_message_cls(
            message_cls=message_cls,
            function_info=function_info,
            field_resolution_by_message_cls=field_resolution_by_message_cls,
        )
        for message_cls in all_message_clss
    }


def _build_function_signature_for_message_cls(
    *,
    message_cls: str,
    function_info: FunctionAccessInfo,
    field_resolution_by_message_cls: dict[str, MessageFieldResolutionLookup],
) -> FunctionAccessSignature:
    normalized_message_type = get_normalized_short_type_name(message_cls)
    self_entries = function_info.accesses_by_cls.get(message_cls, [])
    return FunctionAccessSignature(
        return_role=function_info.get_normalized_return_role(normalized_message_type),
        takes_message_parameter=normalized_message_type in function_info.normalized_parameters,
        size=function_info.size,
        self_accesses=[
            _build_access_atom_signature(entry, field_resolution_by_message_cls) for entry in self_entries
        ],
        foreign_access_summary=_build_foreign_access_inside_summary(
            accesses_by_cls=function_info.accesses_by_cls,
            message_cls=message_cls,
        ),
        opcode_histogram=function_info.opcode_histogram,
        stable_callees=function_info.stable_callees,
        cfg_stats=function_info.cfg_stats,
    )


def _build_short_name_to_cls(
    field_resolution_by_message_cls: dict[str, MessageFieldResolutionLookup],
) -> dict[str, str]:
    by_short_name: dict[str, list[str]] = defaultdict(list)
    for message_cls in field_resolution_by_message_cls:
        short_name = get_normalized_short_type_name(message_cls)
        by_short_name[short_name].append(message_cls)
    return {short_name: clss[0] for short_name, clss in by_short_name.items() if len(clss) == 1}


def _canonicalize_access_kind(access_kind: str) -> str:
    """
    Fold ``address`` into ``read`` so both builds describe a field load the same way.

    Whether a field load shows up as ``mov reg, [obj+off]`` or as ``lea reg, [obj+off]`` depends on
    the IL2CPP codegen of the build, and the two reference builds disagree on it. Left as a kind of
    its own, every such atom would compare as a mismatch against its own counterpart and drag the
    similarity of the messages carrying it down.
    """
    return "read" if access_kind == "address" else access_kind


def _build_access_atom_signature(
    access: AccessEntry,
    field_resolution_by_message_cls: dict[str, MessageFieldResolutionLookup],
) -> AccessAtomSignature:
    if is_field_access_entry(access):
        resolved_field = resolve_field_by_access_entry(access, field_resolution_by_message_cls)
        return AccessAtomSignature(
            entry_type="field",
            access_kind=_canonicalize_access_kind(access.access_kind),
            field_type_shape=resolved_field.field_type_shape,
            field_offset=access.field_offset,
            index_in_function=access.index_in_function,
        )
    return AccessAtomSignature(
        entry_type="typeinfo",
        access_kind=access.access_kind,
        field_offset=None,
        index_in_function=access.index_in_function,
    )


def _build_foreign_access_inside_summary(
    accesses_by_cls: dict[str, list[AccessEntry]],
    message_cls: str,
) -> list[str]:
    return sorted(
        _get_foreign_access_summary_token(access)
        for foreign_cls, foreign_entries in accesses_by_cls.items()
        if foreign_cls != message_cls
        for access in foreign_entries
    )


def _get_foreign_access_summary_token(access: AccessEntry) -> str:
    if is_field_access_entry(access):
        return f"field:{access.access_kind}"
    return f"typeinfo:{access.access_kind}"
