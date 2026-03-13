from collections import Counter

from collections.abc import Mapping

from tests.fixtures.proto_mapper.shapes import NUMBER_SHAPE

from DBDofusUnity.proto_mapper_assembly.field_mapping.field_mapper import build_field_mapping
from DBDofusUnity.proto_mapper_assembly.field_mapping.field_mapping_preparation import prepare_field_mapping_context
from DBDofusUnity.proto_mapper_assembly.helpers.proto_helpers import build_types_by_short_name
from DBDofusUnity.proto_mapper_assembly.interfaces.assembly_access import (
    AccessAtomSignature,
    AccessTraceDocument,
    EnumFunctionResolvedMetadata,
    FieldAccessSignatures,
    MessageAccessSignature,
    TracedFunction,
)
from DBDofusUnity.proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessage, DumpCSMessageField, FieldKey
from DBDofusUnity.proto_mapper_assembly.interfaces.enum_mapping import EnumSignatureEntry
from DBDofusUnity.proto_mapper_assembly.interfaces.field_category import FieldCategoryEnum, FieldTypeShape
from DBDofusUnity.proto_mapper_assembly.interfaces.field_mapping import (
    FieldMappingContext,
    FieldMappingResult,
    MatchingStoreProtocol,
    PreparedFieldMappingContext,
)
from DBDofusUnity.proto_mapper_assembly.interfaces.message_pair import MatchPairKey
from DBDofusUnity.proto_mapper_assembly.interfaces.pinned_pairs import PinnedPair, PinnedPairsConfig
from DBDofusUnity.proto_mapper_assembly.interfaces.signature_overrides import SignatureOverrideEntry
from DBDofusUnity.proto_mapper_assembly.runtime.runtime_store import RuntimeDataStore

NAMESPACE = "Com.Ankama.Dofus.Server.Game.Protocol.Gamemap"
FILE_DESCRIPTOR = "gamemap_reflection"
NEW_NON_OBF_CLS = f"{NAMESPACE}.MapMovementConfirmResponse"
EMPTY_ACCESS_TRACE = AccessTraceDocument(functions_by_address={})


def build_dump_cs(
    class_text: str,
    fd_class_name: str = "GamemapReflection",
    fd_type_def_index: int = 1,
) -> str:
    header = (
        f"public static class {fd_class_name} // TypeDefIndex: {fd_type_def_index}\n"
        "{\n"
        "    public static FileDescriptor Descriptor { get; }\n"
        "}\n\n"
    )
    return header + class_text


def build_dump_cs_by_content(field_line: str) -> str:
    return f"public sealed class Foo : IMessage<Foo> // TypeDefIndex: 1\n{{\n    {field_line}\n}}\n"


def dump_cs_msg(*fields: DumpCSMessageField) -> DumpCSMessage:
    return DumpCSMessage(file_descriptor="FD", name="Msg", fields=list(fields))


def make_message(
    name: str,
    *,
    namespace: str | None = None,
    parent_name: str | None = None,
) -> DumpCSMessage:
    return DumpCSMessage(
        file_descriptor="FD",
        name=name,
        namespace=namespace,
        parent_name=parent_name,
    )


def root_message(name: str) -> DumpCSMessage:
    return DumpCSMessage(file_descriptor="GameReflection", name=name)


def nested_message(parent_name: str, name: str) -> DumpCSMessage:
    return DumpCSMessage(file_descriptor="GameReflection", name=name, parent_name=parent_name)


def field_signature(
    field_offset: int,
    field_type_shape: FieldTypeShape | None = NUMBER_SHAPE,
    *,
    field_key: FieldKey | None = None,
    accesses: list[AccessAtomSignature] | None = None,
) -> FieldAccessSignatures:
    return FieldAccessSignatures(
        field_key=field_key or FieldKey(field_offset, f"field_{field_offset}_"),
        field_type_shape=field_type_shape or NUMBER_SHAPE,
        accesses=accesses or [],
    )


def message_signature(
    message_cls: str,
    declared_field_signatures: list[DumpCSMessageField] | dict[FieldKey, DumpCSMessageField],
    field_signatures: list[FieldAccessSignatures] | None = None,
    *,
    live_field_keys: frozenset[FieldKey] = frozenset(),
    dump_cs_msg: DumpCSMessage | None = None,
) -> MessageAccessSignature:
    if dump_cs_msg is not None:
        message = dump_cs_msg
        resolved_live_field_keys = live_field_keys or frozenset(
            field.field_key for field in dump_cs_msg.fields
        )
    else:
        declared_fields = _declared_signature_fields(declared_field_signatures)
        message = DumpCSMessage(
            file_descriptor="GameReflection",
            name="Message",
            fields=list(declared_fields),
        )
        resolved_live_field_keys = live_field_keys or frozenset(field.field_key for field in declared_fields)
    resolved_field_signatures = _resolve_field_signatures(
        message=message,
        field_signatures=field_signatures or [],
        live_field_keys=resolved_live_field_keys,
    )
    return MessageAccessSignature(
        message_cls=message_cls,
        file_descriptor=message.file_descriptor,
        dump_cs_msg=message,
        function_signatures=[],
        field_signatures=resolved_field_signatures,
    )


def make_message_signature(
    message: DumpCSMessage,
    *,
    live_field_keys: frozenset[FieldKey] = frozenset(),
    field_signatures: list[FieldAccessSignatures] | None = None,
) -> MessageAccessSignature:
    resolved_field_signatures = _resolve_field_signatures(
        message=message,
        field_signatures=field_signatures or [],
        live_field_keys=live_field_keys,
    )
    return MessageAccessSignature(
        message_cls=message.composed_name,
        file_descriptor=message.file_descriptor,
        dump_cs_msg=message,
        function_signatures=[],
        field_signatures=resolved_field_signatures,
    )


def _resolve_field_signatures(
    *,
    message: DumpCSMessage,
    field_signatures: list[FieldAccessSignatures],
    live_field_keys: frozenset[FieldKey],
) -> list[FieldAccessSignatures]:
    fields_by_key = {field.field_key: field for field in message.fields}
    live_fields_by_offset: dict[int, list[DumpCSMessageField]] = {}
    for live_field_key in live_field_keys:
        live_field = fields_by_key.get(live_field_key)
        if live_field is None:
            continue
        live_fields_by_offset.setdefault(live_field.memory_offset, []).append(live_field)

    resolved_field_signatures: list[FieldAccessSignatures] = []
    covered_field_keys: set[FieldKey] = set()
    for input_signature in field_signatures:
        resolved_field = fields_by_key.get(input_signature.field_key)
        if resolved_field is None:
            candidates = live_fields_by_offset.get(input_signature.field_offset, [])
            resolved_field = candidates[0] if candidates else None
        if resolved_field is None:
            resolved_field_signatures.append(input_signature)
            covered_field_keys.add(input_signature.field_key)
            continue
        resolved_field_signatures.append(
            input_signature.model_copy(update={"field_key": resolved_field.field_key})
        )
        covered_field_keys.add(resolved_field.field_key)

    for live_field_key in live_field_keys - covered_field_keys:
        live_field = fields_by_key.get(live_field_key)
        if live_field is None:
            continue
        resolved_field_signatures.append(
            FieldAccessSignatures(
                field_key=live_field.field_key,
                field_type_shape=live_field.field_type_shape,
                accesses=[],
            )
        )
    return resolved_field_signatures


def _declared_signature_fields(
    declared_field_signatures: list[DumpCSMessageField] | dict[FieldKey, DumpCSMessageField],
) -> tuple[DumpCSMessageField, ...]:
    if isinstance(declared_field_signatures, dict):
        return tuple(
            field.model_copy(
                update={
                    "memory_offset": field_key.memory_offset,
                    "field_name": field_key.field_name,
                    "property_name": field.property_name or field_key.field_name.rstrip("_"),
                }
            )
            for field_key, field in declared_field_signatures.items()
        )
    return tuple(
        field.model_copy(
            update={
                "memory_offset": index,
                "field_name": f"field_{index}_",
                "property_name": f"Field{index}",
            }
        )
        for index, field in enumerate(declared_field_signatures)
    )


def make_obf_message_with_unmapped_field() -> tuple[DumpCSMessage, DumpCSMessageField]:
    sleeping_field = DumpCSMessageField(
        clr_type="Int32",
        normalized_type="Int32",
        category=FieldCategoryEnum.NUMBER,
        memory_offset=0x10,
        field_name="sleeper_",
        property_name="Sleeper",
    )
    message = DumpCSMessage(file_descriptor="FD", name="obf_msg", fields=[sleeping_field])
    return message, sleeping_field


def make_non_obf_signature() -> MessageAccessSignature:
    non_obf_field = DumpCSMessageField(
        clr_type="Int32",
        normalized_type="Int32",
        category=FieldCategoryEnum.NUMBER,
        memory_offset=0x10,
        field_name="sleeper_",
        property_name="Sleeper",
    )
    message = DumpCSMessage(file_descriptor="FD", name="NonObfMsg", fields=[non_obf_field])
    return make_message_signature(message)


def build_message_lookup(messages: list[DumpCSMessage]) -> dict[str, DumpCSMessage]:
    return {message.composed_name: message for message in messages}


def make_field_mapping_context(
    runtime_data_store: RuntimeDataStore,
    *,
    score_by_pair: Mapping[MatchPairKey, float] | None = None,
    signature_overrides_by_non_obf_cls: Mapping[str, SignatureOverrideEntry] | None = None,
    obf_enum_signatures_by_name: Mapping[str, EnumSignatureEntry] | None = None,
    non_obf_enum_signatures_by_name: Mapping[str, EnumSignatureEntry] | None = None,
    obf_access_trace: AccessTraceDocument | None = None,
    non_obf_access_trace: AccessTraceDocument | None = None,
) -> FieldMappingContext:
    resolved_overrides = signature_overrides_by_non_obf_cls or {}
    resolved_obf_enum_signatures = dict(obf_enum_signatures_by_name or {})
    resolved_non_obf_enum_signatures = dict(non_obf_enum_signatures_by_name or {})
    hint_enum_signatures = {
        hint.non_obf_enum_type: hint.signature
        for override in resolved_overrides.values()
        for hints_by_slot in override.enum_signature_hints_by_non_obf_prop_name.values()
        for hint in hints_by_slot.values()
    }
    obf_enum_signatures_for_trace = {**resolved_obf_enum_signatures, **hint_enum_signatures}
    non_obf_enum_signatures_for_trace = {**resolved_non_obf_enum_signatures, **hint_enum_signatures}
    return FieldMappingContext(
        runtime_data_store=runtime_data_store,
        score_by_pair=score_by_pair if score_by_pair is not None else {},
        signature_overrides_by_non_obf_cls=resolved_overrides,
        obf_enum_signatures_by_name=resolved_obf_enum_signatures,
        non_obf_enum_signatures_by_name=resolved_non_obf_enum_signatures,
        obf_access_trace=obf_access_trace
        if obf_access_trace is not None
        else build_minimal_enum_trace_document(obf_enum_signatures_for_trace),
        non_obf_access_trace=non_obf_access_trace
        if non_obf_access_trace is not None
        else build_minimal_enum_trace_document(non_obf_enum_signatures_for_trace),
    )


def build_field_mapping_for_test(
    non_obf_signature: MessageAccessSignature,
    obf_signature: MessageAccessSignature,
    non_obf_messages_by_cls: dict[str, DumpCSMessage],
    obf_messages_by_cls: dict[str, DumpCSMessage],
    *,
    matching_store: MatchingStoreProtocol | None = None,
    field_mapping_context: FieldMappingContext,
    obf_type_index: dict[str, tuple[DumpCSMessage, ...]] | None = None,
    non_obf_type_index: dict[str, tuple[DumpCSMessage, ...]] | None = None,
    pinned_pair: PinnedPair | None = None,
) -> FieldMappingResult:
    return build_field_mapping(
        non_obf_signature=non_obf_signature,
        obf_signature=obf_signature,
        non_obf_messages_by_cls=non_obf_messages_by_cls,
        obf_messages_by_cls=obf_messages_by_cls,
        matching_store=matching_store,
        field_mapping_context=field_mapping_context,
        obf_type_index=obf_type_index
        if obf_type_index is not None
        else build_types_by_short_name(obf_messages_by_cls),
        non_obf_type_index=non_obf_type_index
        if non_obf_type_index is not None
        else build_types_by_short_name(non_obf_messages_by_cls),
        pinned_pair=pinned_pair,
    )


def prepare_field_mapping_context_for_test(
    *,
    non_obf_signature: MessageAccessSignature,
    obf_signature: MessageAccessSignature,
    field_mapping_context: FieldMappingContext,
    non_obf_messages: list[DumpCSMessage] | None = None,
    obf_messages: list[DumpCSMessage] | None = None,
    matching_store: MatchingStoreProtocol | None = None,
    obf_type_index: dict[str, tuple[DumpCSMessage, ...]] | None = None,
    non_obf_type_index: dict[str, tuple[DumpCSMessage, ...]] | None = None,
    pinned_pair: PinnedPair | None = None,
) -> PreparedFieldMappingContext:
    non_obf_message_lookup = build_message_lookup(non_obf_messages or [non_obf_signature.dump_cs_msg])
    obf_message_lookup = build_message_lookup(obf_messages or [obf_signature.dump_cs_msg])
    return prepare_field_mapping_context(
        non_obf_signature=non_obf_signature,
        obf_signature=obf_signature,
        non_obf_messages_by_cls=non_obf_message_lookup,
        obf_messages_by_cls=obf_message_lookup,
        matching_store=matching_store,
        field_mapping_context=field_mapping_context,
        obf_type_index=obf_type_index if obf_type_index is not None else {},
        non_obf_type_index=non_obf_type_index if non_obf_type_index is not None else {},
        pinned_pair=pinned_pair,
    )


def build_verified_mapping() -> PinnedPairsConfig:
    return PinnedPairsConfig(pairs=[])


def existing_non_obf_msg() -> DumpCSMessage:
    return DumpCSMessage(file_descriptor=FILE_DESCRIPTOR, name="SomeExistingMsg", namespace=NAMESPACE)


def bootstrap_non_obf_msg(
    *,
    non_obf_cls: str = NEW_NON_OBF_CLS,
    fields: list[DumpCSMessageField] | None = None,
) -> DumpCSMessage:
    namespace, _, name = non_obf_cls.rpartition(".")
    return DumpCSMessage(
        file_descriptor=FILE_DESCRIPTOR,
        name=name,
        namespace=namespace or None,
        fields=[] if fields is None else fields,
    )


def build_minimal_enum_trace_document(
    enum_signatures_by_name: dict[str, EnumSignatureEntry],
) -> AccessTraceDocument:
    function_addresses = {
        called_function.function_address
        for enum_signature in enum_signatures_by_name.values()
        for switch_pattern in enum_signature.switch_patterns
        for member_group in switch_pattern.member_groups
        for called_function in member_group.called_functions
    }
    return AccessTraceDocument(
        functions_by_address={
            function_address: TracedFunction(
                start_address=int(function_address, 16),
                end_address=int(function_address, 16),
                size=0,
                access_infos=[],
                opcode_histogram=Counter(),
                aliases=[],
                stable_callees=[],
                cfg_stats=None,
                resolved_metadata=EnumFunctionResolvedMetadata(
                    resolution_kind="unknown",
                    raw_name=None,
                    raw_signature=None,
                    return_type=None,
                    parameter_types=[],
                    return_kind="unknown",
                    parameter_kinds=[],
                ),
            )
            for function_address in function_addresses
        },
        enum_signatures_by_name=enum_signatures_by_name,
    )
