from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Literal

from tests.test_dbdofus_unity.test_proto_mapper_assembly.fixture.shapes import NUMBER_SHAPE

from proto_mapper_assembly.controllers.access_signatures import build_message_access_signatures_by_cls
from proto_mapper_assembly.controllers.message_fields import build_message_field_resolution_lookup
from proto_mapper_assembly.interfaces.assembly_access import (
    AccessAtomSignature,
    AccessEntry,
    AccessKind,
    AccessTraceDocument,
    FieldAccessEntry,
    FieldAccessSignatures,
    FunctionAccessInfo,
    FunctionAccessSignature,
    HandlerRegistrationAccessEntry,
    MessageAccessSignature,
    ProtoAccessesInfo,
    ReturnRole,
    TypeInfoAccessEntry,
)
from proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessage, DumpCSMessageField, FieldKey
from proto_mapper_assembly.interfaces.enum_mapping import EnumSignatureEntry, EnumSwitchPattern
from proto_mapper_assembly.interfaces.field_category import (
    FieldCategoryEnum,
    FieldTypeLeafKind,
    FieldTypeShape,
)
from proto_mapper_assembly.interfaces.function_access_signature import CfgStats
from proto_mapper_assembly.interfaces.message_field_resolution_lookup import MessageFieldResolutionLookup
from proto_mapper_assembly.scoring.message_scoring import StructureSimilarityContext

DEFAULT_CFG_STATS = CfgStats(basic_block_count=4, edge_count=4, back_edge_count=0, max_block_depth=2)


def access_atom(
    *,
    entry_type: Literal["field", "typeinfo"] = "field",
    access_kind: str = "read",
    field_type_shape: FieldTypeShape | None = None,
    field_offset: int | None = 24,
    field_access_index: int = 0,
) -> AccessAtomSignature:
    return AccessAtomSignature(
        entry_type=entry_type,
        access_kind=access_kind,
        field_type_shape=field_type_shape,
        field_offset=field_offset,
        index_in_function=field_access_index,
    )


def builder_function_access_signature(
    *,
    return_role: ReturnRole = ReturnRole.SELF,
    takes_message_parameter: bool = True,
    size: int = 200,
    self_accesses: list[AccessAtomSignature] | None = None,
    foreign_access_summary: list[str] | None = None,
    stable_callees: list[str] | None = None,
    cfg_stats: CfgStats | None = None,
) -> FunctionAccessSignature:
    return FunctionAccessSignature(
        return_role=return_role,
        takes_message_parameter=takes_message_parameter,
        size=size,
        self_accesses=self_accesses or [],
        foreign_access_summary=foreign_access_summary or [],
        opcode_histogram=Counter(),
        stable_callees=stable_callees or [],
        cfg_stats=cfg_stats,
    )


def field_access_signature(
    *,
    field_offset: int = 24,
    field_key: FieldKey | None = None,
    field_type_shape: FieldTypeShape | None = NUMBER_SHAPE,
    accesses: list[AccessAtomSignature] | None = None,
    is_traced: bool = True,
) -> FieldAccessSignatures:
    return FieldAccessSignatures(
        field_key=field_key or FieldKey(field_offset, f"field_{field_offset}_"),
        field_type_shape=field_type_shape or NUMBER_SHAPE,
        accesses=accesses or [],
        is_traced=is_traced,
    )


def declared_field_signature(
    field_type_shape: FieldTypeShape = NUMBER_SHAPE,
    *,
    is_oneof_member: bool = False,
    enum_types_by_slot: dict[str, str] | None = None,
) -> DumpCSMessageField:
    enum_types = enum_types_by_slot or {}
    return DumpCSMessageField(
        clr_type=_clr_type_from_shape(field_type_shape),
        normalized_type=_normalized_type_from_shape(field_type_shape),
        category=field_type_shape.category,
        memory_offset=0,
        field_name="field_0_",
        property_name="Field0",
        oneof_group_name="Choice" if is_oneof_member else None,
        is_synthetic_oneof_variant=is_oneof_member,
        enum_key_type=enum_types.get("key"),
        enum_value_type=enum_types.get("value"),
    )


def _clr_type_from_shape(field_type_shape: FieldTypeShape) -> str:
    if field_type_shape.category == FieldCategoryEnum.NUMBER:
        return "Int32"
    if field_type_shape.category == FieldCategoryEnum.BOOLEAN:
        return "Boolean"
    if field_type_shape.category == FieldCategoryEnum.STRING:
        return "String"
    if field_type_shape.category == FieldCategoryEnum.ENUM:
        return "SomeEnum"
    if field_type_shape.category == FieldCategoryEnum.REPEATED:
        return f"RepeatedField<{_normalized_type_from_leaf(field_type_shape.inner_kind)}>"
    if field_type_shape.category == FieldCategoryEnum.MAP:
        key_type = _normalized_type_from_leaf(field_type_shape.inner_kind)
        value_type = _normalized_type_from_leaf(field_type_shape.outer_kind)
        return f"MapField<{key_type}, {value_type}>"
    return _normalized_type_from_shape(field_type_shape)


def _normalized_type_from_shape(field_type_shape: FieldTypeShape) -> str:
    if field_type_shape.category == FieldCategoryEnum.REPEATED:
        return f"RepeatedField<{_normalized_type_from_leaf(field_type_shape.inner_kind)}>"
    if field_type_shape.category == FieldCategoryEnum.MAP:
        key_type = _normalized_type_from_leaf(field_type_shape.inner_kind)
        value_type = _normalized_type_from_leaf(field_type_shape.outer_kind)
        return f"MapField<{key_type}, {value_type}>"
    return _normalized_type_from_leaf(field_type_shape.inner_kind) or _clr_type_from_shape(field_type_shape)


def _normalized_type_from_leaf(field_type_leaf: FieldTypeLeafKind | None) -> str:
    if field_type_leaf == FieldTypeLeafKind.NUMBER:
        return "Int32"
    if field_type_leaf == FieldTypeLeafKind.BOOLEAN:
        return "Boolean"
    if field_type_leaf == FieldTypeLeafKind.STRING:
        return "String"
    if field_type_leaf == FieldTypeLeafKind.ENUM:
        return "SomeEnum"
    if field_type_leaf == FieldTypeLeafKind.ANY:
        return "Object"
    if field_type_leaf == FieldTypeLeafKind.ONEOF:
        return "Object"
    if field_type_leaf == FieldTypeLeafKind.MESSAGE:
        return "ChildMessage"
    return "Int32"


def _declared_signature_fields(
    declared_field_signatures: list[DumpCSMessageField] | dict[FieldKey, DumpCSMessageField] | None,
) -> tuple[DumpCSMessageField, ...]:
    if declared_field_signatures is None:
        return ()
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


def access_message_signature(
    *,
    message_cls: str = "Message",
    file_descriptor: str = "FD",
    function_signatures: list[FunctionAccessSignature] | None = None,
    field_signatures: list[FieldAccessSignatures] | None = None,
    declared_field_signatures: list[DumpCSMessageField] | dict[FieldKey, DumpCSMessageField] | None = None,
    live_field_keys: frozenset[FieldKey] = frozenset(),
) -> MessageAccessSignature:
    declared_fields = _declared_signature_fields(declared_field_signatures)
    dump_cs_msg = DumpCSMessage(
        file_descriptor=file_descriptor,
        name=message_cls.rsplit(".", maxsplit=1)[-1],
        namespace=message_cls.rsplit(".", maxsplit=1)[0] or None if "." in message_cls else None,
        fields=list(declared_fields),
    )
    resolved_live_field_keys = live_field_keys or frozenset(field.field_key for field in declared_fields)
    resolved_field_signatures = _resolve_access_field_signatures(
        declared_fields=declared_fields,
        field_signatures=field_signatures or [],
        live_field_keys=resolved_live_field_keys,
    )
    return MessageAccessSignature(
        message_cls=message_cls,
        file_descriptor=file_descriptor,
        dump_cs_msg=dump_cs_msg,
        function_signatures=function_signatures or [],
        field_signatures=resolved_field_signatures,
    )


def _resolve_access_field_signatures(
    *,
    declared_fields: tuple[DumpCSMessageField, ...],
    field_signatures: list[FieldAccessSignatures],
    live_field_keys: frozenset[FieldKey],
) -> list[FieldAccessSignatures]:
    declared_fields_by_key = {field.field_key: field for field in declared_fields}
    live_fields_by_offset: dict[int, list[DumpCSMessageField]] = {}
    for live_field_key in live_field_keys:
        live_field = declared_fields_by_key.get(live_field_key)
        if live_field is None:
            continue
        live_fields_by_offset.setdefault(live_field.memory_offset, []).append(live_field)

    resolved_signatures: list[FieldAccessSignatures] = []
    covered_field_keys: set[FieldKey] = set()
    for field_signature in field_signatures:
        candidates = live_fields_by_offset.get(field_signature.field_offset, [])
        resolved_field = (
            candidates[0] if candidates else declared_fields_by_key.get(field_signature.field_key)
        )
        if resolved_field is None:
            resolved_signatures.append(field_signature)
            covered_field_keys.add(field_signature.field_key)
            continue
        resolved_signatures.append(field_signature.model_copy(update={"field_key": resolved_field.field_key}))
        covered_field_keys.add(resolved_field.field_key)

    for live_field_key in live_field_keys - covered_field_keys:
        live_field = declared_fields_by_key.get(live_field_key)
        if live_field is None:
            continue
        resolved_signatures.append(
            FieldAccessSignatures(
                field_key=live_field.field_key,
                field_type_shape=live_field.field_type_shape,
                accesses=[],
            )
        )
    return resolved_signatures


def builder_structure_similarity_context(
    *,
    left_signatures: list[MessageAccessSignature],
    right_signatures: list[MessageAccessSignature],
    left_enum_signatures_by_name: dict[str, EnumSignatureEntry] | None = None,
    right_enum_signatures_by_name: dict[str, EnumSignatureEntry] | None = None,
    left_access_trace: AccessTraceDocument | None = None,
    right_access_trace: AccessTraceDocument | None = None,
) -> StructureSimilarityContext:
    return StructureSimilarityContext(
        left_signatures_by_cls={signature.message_cls: signature for signature in left_signatures},
        right_signatures_by_cls={signature.message_cls: signature for signature in right_signatures},
        left_enum_signatures_by_name=left_enum_signatures_by_name or {},
        right_enum_signatures_by_name=right_enum_signatures_by_name or {},
        left_access_trace=left_access_trace
        if left_access_trace is not None
        else AccessTraceDocument(functions_by_address={}),
        right_access_trace=right_access_trace
        if right_access_trace is not None
        else AccessTraceDocument(functions_by_address={}),
    )


def builder_field_access_entry(
    *,
    cls: str,
    field: str = "raw_field",
    access_kind: AccessKind = "read",
    property_name: str | None = None,
    field_offset: int | None = 24,
    instruction_address: int = 0,
    index_in_function: int = 0,
) -> FieldAccessEntry:
    resolved_property_name = property_name
    resolved_field_offset = field_offset
    if access_kind in {"getter", "setter"}:
        resolved_property_name = property_name or field
        resolved_field_offset = None
    return FieldAccessEntry(
        type="field",
        access_kind=access_kind,
        cls=cls,
        field_name=field,
        property_name=resolved_property_name,
        field_offset=resolved_field_offset,
        instruction_address=instruction_address,
        index_in_function=index_in_function,
    )


def builder_typeinfo_access_entry(
    *,
    cls: str,
    instruction_address: int = 0,
    target_address: int = 0,
    index_in_function: int = 0,
) -> TypeInfoAccessEntry:
    return TypeInfoAccessEntry(
        type="typeinfo",
        access_kind="load",
        cls=cls,
        instruction_address=instruction_address,
        target_address=target_address,
        index_in_function=index_in_function,
    )


def builder_handler_registration_access_entry(
    *,
    cls: str,
    handler_method: str = "Boolean Handle(Message)",
    method_info_address: int = 0x1000,
    filter_typeinfo_address: int = 0x2000,
    instruction_address: int = 0,
    index_in_function: int = 0,
    handler_function_address: int | None = 0x3000,
    registration_ordinal: int = 0,
) -> HandlerRegistrationAccessEntry:
    return HandlerRegistrationAccessEntry(
        type="handler_registration",
        access_kind="register",
        cls=cls,
        handler_method=handler_method,
        method_info_address=method_info_address,
        filter_typeinfo_address=filter_typeinfo_address,
        instruction_address=instruction_address,
        index_in_function=index_in_function,
        handler_function_address=handler_function_address,
        registration_ordinal=registration_ordinal,
    )


def function_access_info(
    *,
    name: str = "Mapper::Void Run(Message)",
    parameters: Sequence[str] = ("Message",),
    return_type: str = "Void",
    start_address: int = 0,
    end_address: int = 80,
    size: int = 80,
    group: str = "Core.dll/Mapper",
    access_infos: Sequence[AccessEntry] = (),
    stable_callees: Sequence[str] = (),
    cfg_stats: CfgStats = DEFAULT_CFG_STATS,
) -> FunctionAccessInfo:
    return FunctionAccessInfo(
        name=name,
        parameters=list(parameters),
        return_type=return_type,
        start_address=start_address,
        end_address=end_address,
        size=size,
        group=group,
        access_infos=list(access_infos),
        opcode_histogram=Counter(),
        stable_callees=list(stable_callees),
        cfg_stats=cfg_stats,
    )


def build_proto_accesses(*functions: FunctionAccessInfo) -> ProtoAccessesInfo:
    return ProtoAccessesInfo(root={function.name: function for function in functions})


def stub_message(
    composed_name: str,
    *,
    field_offsets: Sequence[int] = (),
    property_names: Sequence[str] = (),
) -> DumpCSMessage:
    namespace, separator, name = composed_name.rpartition(".")
    fields: list[DumpCSMessageField] = [
        DumpCSMessageField(
            clr_type="Int32",
            normalized_type="Int32",
            category=FieldCategoryEnum.NUMBER,
            memory_offset=field_offset,
            field_name=f"field_{field_offset}_",
            property_name=f"Field{field_offset}",
        )
        for field_offset in sorted(set(field_offsets))
    ]
    used_offsets = {field.memory_offset for field in fields}
    next_offset = max(used_offsets) + 8 if used_offsets else 0x100
    for property_name in sorted(set(property_names)):
        fields.append(
            DumpCSMessageField(
                clr_type="Int32",
                normalized_type="Int32",
                category=FieldCategoryEnum.NUMBER,
                memory_offset=next_offset,
                field_name=property_name.lower() + "_",
                property_name=property_name,
            )
        )
        next_offset += 8
    return DumpCSMessage(
        file_descriptor="FD",
        name=name if separator else composed_name,
        namespace=namespace or None,
        fields=fields,
    )


def build_file_descriptor_lookup(
    *message_classes: str,
    overrides: dict[str, str] | None = None,
    field_offsets_by_cls: Mapping[str, Sequence[int]] | None = None,
    property_names_by_cls: Mapping[str, Sequence[str]] | None = None,
) -> dict[str, DumpCSMessage]:
    offsets_by_cls = field_offsets_by_cls or {}
    property_names = property_names_by_cls or {}
    lookup = {
        message_cls: stub_message(
            message_cls,
            field_offsets=offsets_by_cls.get(message_cls, ()),
            property_names=property_names.get(message_cls, ()),
        )
        for message_cls in message_classes
    }
    if overrides is not None:
        for message_cls, file_descriptor in overrides.items():
            lookup[message_cls] = lookup[message_cls].model_copy(update={"file_descriptor": file_descriptor})
    return lookup


def build_field_resolution_lookup(
    *messages: DumpCSMessage,
) -> dict[str, MessageFieldResolutionLookup]:
    return build_message_field_resolution_lookup(list(messages))


def stub_resolution_lookup(
    *message_classes: str,
    field_offsets_by_cls: Mapping[str, Sequence[int]] | None = None,
    property_names_by_cls: Mapping[str, Sequence[str]] | None = None,
) -> dict[str, MessageFieldResolutionLookup]:
    offsets_by_cls = field_offsets_by_cls or {}
    property_names = property_names_by_cls or {}
    return build_field_resolution_lookup(
        *(
            stub_message(
                cls,
                field_offsets=offsets_by_cls.get(cls, ()),
                property_names=property_names.get(cls, ()),
            )
            for cls in message_classes
        )
    )


def _collect_field_offsets_by_cls(
    functions: Sequence[FunctionAccessInfo],
) -> dict[str, list[int]]:
    offsets_by_cls: dict[str, list[int]] = {}
    for function in functions:
        for access in function.access_infos:
            if access.type != "field" or access.field_offset is None:
                continue
            offsets_by_cls.setdefault(access.cls, []).append(access.field_offset)
    return offsets_by_cls


def _collect_property_names_by_cls(
    functions: Sequence[FunctionAccessInfo],
) -> dict[str, list[str]]:
    names_by_cls: dict[str, list[str]] = {}
    for function in functions:
        for access in function.access_infos:
            if access.type != "field" or access.property_name is None:
                continue
            names_by_cls.setdefault(access.cls, []).append(access.property_name)
    return names_by_cls


def _augment_message_with_missing_fields(
    message: DumpCSMessage,
    offsets_by_cls: dict[str, list[int]],
    property_names_by_cls: dict[str, list[str]],
) -> DumpCSMessage:
    needed_offsets = set(offsets_by_cls.get(message.composed_name, ()))
    existing_offsets = {field.memory_offset for field in message.fields}
    missing_offsets = sorted(needed_offsets - existing_offsets)

    needed_property_names = set(property_names_by_cls.get(message.composed_name, ()))
    existing_property_names = {field.property_name for field in message.fields if field.property_name}
    missing_property_names = sorted(needed_property_names - existing_property_names)

    if not missing_offsets and not missing_property_names:
        return message

    used_offsets = existing_offsets | set(missing_offsets)
    starting_offset = max(used_offsets) + 8 if used_offsets else 0x100
    extra_fields: list[DumpCSMessageField] = [
        DumpCSMessageField(
            clr_type="Int32",
            normalized_type="Int32",
            category=FieldCategoryEnum.NUMBER,
            memory_offset=offset,
            field_name=f"field_{offset}_",
            property_name=f"Field{offset}",
        )
        for offset in missing_offsets
    ]
    extra_fields.extend(
        DumpCSMessageField(
            clr_type="Int32",
            normalized_type="Int32",
            category=FieldCategoryEnum.NUMBER,
            memory_offset=starting_offset + 8 * index,
            field_name=property_name.lower() + "_",
            property_name=property_name,
        )
        for index, property_name in enumerate(missing_property_names)
    )
    return message.model_copy(update={"fields": list(message.fields) + extra_fields})


def build_access_signatures_for_test(
    *functions: FunctionAccessInfo,
    message_classes: Sequence[str] = (),
    messages: Sequence[DumpCSMessage] = (),
    enum_signatures: dict[str, EnumSignatureEntry] | None = None,
) -> dict[str, MessageAccessSignature]:
    offsets_by_cls = _collect_field_offsets_by_cls(functions)
    property_names_by_cls = _collect_property_names_by_cls(functions)
    if messages:
        augmented = [
            _augment_message_with_missing_fields(message, offsets_by_cls, property_names_by_cls)
            for message in messages
        ]
        dump_lookup = {message.composed_name: message for message in augmented}
        resolution_lookup = build_field_resolution_lookup(*augmented)
    else:
        dump_lookup = build_file_descriptor_lookup(
            *message_classes,
            field_offsets_by_cls=offsets_by_cls,
            property_names_by_cls=property_names_by_cls,
        )
        resolution_lookup = stub_resolution_lookup(
            *message_classes,
            field_offsets_by_cls=offsets_by_cls,
            property_names_by_cls=property_names_by_cls,
        )

    return build_message_access_signatures_by_cls(
        build_proto_accesses(*functions),
        dump_lookup,
        resolution_lookup,
        enum_signatures=enum_signatures or {},
    )


def enum_signature_entry(*, field_offset: int, members: dict[str, str] | None = None) -> EnumSignatureEntry:
    return EnumSignatureEntry(
        member_value_to_name=members or {"0": "UNKNOWN"},
        switch_patterns=[
            EnumSwitchPattern(function_addr=0x1000, field_offset=field_offset, member_groups=[])
        ],
    )
