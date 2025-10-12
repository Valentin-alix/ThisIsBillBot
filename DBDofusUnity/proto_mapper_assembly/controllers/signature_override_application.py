from __future__ import annotations

from DBDofusUnity.proto_mapper_assembly.controllers.enum_signatures import validate_enum_signature_member_values
from DBDofusUnity.proto_mapper_assembly.controllers.message_fields import (
    bind_field_signatures_to_message_fields,
    build_dump_cs_field_lookup,
)
from DBDofusUnity.proto_mapper_assembly.interfaces.assembly_access import FieldAccessSignatures, MessageAccessSignature
from DBDofusUnity.proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessage, normalize_proto_field_name
from DBDofusUnity.proto_mapper_assembly.interfaces.enum_mapping import EnumSignatureEntry
from DBDofusUnity.proto_mapper_assembly.interfaces.signature_overrides import FieldOverrideBinding, SignatureOverrideEntry


def validate_stored_field_bindings(
    *,
    non_obf_cls: str,
    non_obf_message: DumpCSMessage,
    obf_field_binding_by_non_obf_property_name: dict[str, FieldOverrideBinding],
    field_signatures_by_non_obf_property_name: dict[str, FieldAccessSignatures],
) -> frozenset[str]:
    incompatible_property_names: set[str] = set()
    non_obf_fields_by_name = build_dump_cs_field_lookup(non_obf_message)
    for (
        non_obf_property_name,
        obf_field_binding,
    ) in obf_field_binding_by_non_obf_property_name.items():
        normalized_field_name = normalize_proto_field_name(non_obf_property_name)
        non_obf_field = non_obf_fields_by_name.get(normalized_field_name)
        if non_obf_field is None:
            message = (
                "Cannot apply stored field binding for "
                f"{non_obf_cls}: unknown field {non_obf_property_name!r}"
            )
            raise ValueError(message)

        obf_field_signature = field_signatures_by_non_obf_property_name.get(non_obf_property_name)
        if obf_field_signature is None:
            message = (
                "Invalid stored field binding for "
                f"{non_obf_cls}: no field signature for {non_obf_property_name!r}"
            )
            raise ValueError(message)

        if obf_field_signature.field_offset != obf_field_binding.obf_memory_offset:
            message = (
                "Invalid stored field binding for "
                f"{non_obf_cls}: field signature offset does not match "
                f"{non_obf_property_name!r}"
            )
            raise ValueError(message)

        if obf_field_signature.field_key.field_name != non_obf_field.field_name:
            message = (
                "Invalid stored field binding for "
                f"{non_obf_cls}: field signature key does not match "
                f"{non_obf_property_name!r}"
            )
            raise ValueError(message)

        if obf_field_signature.field_type_shape != non_obf_field.field_type_shape:
            incompatible_property_names.add(non_obf_property_name)

    return frozenset(incompatible_property_names)


def validate_stored_enum_signature_hints(
    *,
    non_obf_cls: str,
    non_obf_message: DumpCSMessage,
    override: SignatureOverrideEntry,
    non_obf_enum_signatures_by_name: dict[str, EnumSignatureEntry],
) -> None:
    non_obf_fields_by_name = build_dump_cs_field_lookup(non_obf_message)
    for (
        non_obf_prop_name,
        enum_signature_hints_by_slot,
    ) in override.enum_signature_hints_by_non_obf_prop_name.items():
        normalized_field_name = normalize_proto_field_name(non_obf_prop_name)
        non_obf_field = non_obf_fields_by_name.get(normalized_field_name)
        if non_obf_field is None:
            message = (
                "Cannot apply stored enum signature hint for "
                f"{non_obf_cls}: unknown field {non_obf_prop_name!r}"
            )
            raise ValueError(message)

        for enum_slot, enum_signature_hint in enum_signature_hints_by_slot.items():
            field_enum_types = non_obf_field.enum_field_types
            field_enum_type = field_enum_types.key if enum_slot == "key" else field_enum_types.value
            if field_enum_type is None or enum_signature_hint.non_obf_enum_type != field_enum_type:
                message = (
                    "Invalid stored enum signature hint for "
                    f"{non_obf_cls}: enum type mismatch for {non_obf_prop_name!r} slot {enum_slot!r}"
                )
                raise ValueError(message)

            validate_enum_signature_member_values(enum_signature_hint.signature)
            non_obf_enum_signature = non_obf_enum_signatures_by_name.get(
                enum_signature_hint.non_obf_enum_type
            )
            if non_obf_enum_signature is None:
                continue

            canonical_member_values = set(non_obf_enum_signature.member_value_to_name)
            invalid_member_values = [
                member_value
                for member_value in enum_signature_hint.signature.member_value_to_name
                if member_value not in canonical_member_values
            ]
            if invalid_member_values:
                message = (
                    "Invalid stored enum signature hint for "
                    f"{non_obf_cls}: unknown enum member values for "
                    f"{non_obf_prop_name!r} slot {enum_slot!r}: "
                    f"{sorted(invalid_member_values, key=int)}"
                )
                raise ValueError(message)


def apply_stored_signature_overrides(
    non_obf_signatures_by_cls: dict[str, MessageAccessSignature],
    overrides: dict[str, SignatureOverrideEntry],
    non_obf_enum_signatures_by_name: dict[str, EnumSignatureEntry],
) -> dict[str, MessageAccessSignature]:
    """
    Return a copy of non_obf_signatures_by_cls with stored JSON overrides applied.

    For each non-obf class in overrides:
    - function_signatures are replaced with OBF ones.
    - field_signatures are merged: override entries (OBF offsets) take priority; original
      non-obf entries are kept for fields not present in the override.
    - If field bindings are provided, dump_cs_msg field memory_offsets and
      field signature identities are updated to align with the OBF struct layout so that
      non_obf_field.memory_offset matches the keys in field_signatures.
    """
    result = dict(non_obf_signatures_by_cls)
    for non_obf_cls, override in overrides.items():
        non_obf_sig = result.get(non_obf_cls)
        if non_obf_sig is None:
            continue

        validate_stored_field_bindings(
            non_obf_cls=non_obf_cls,
            non_obf_message=non_obf_sig.dump_cs_msg,
            obf_field_binding_by_non_obf_property_name=(override.obf_field_binding_by_non_obf_property_name),
            field_signatures_by_non_obf_property_name=override.field_signatures,
        )
        validate_stored_enum_signature_hints(
            non_obf_cls=non_obf_cls,
            non_obf_message=non_obf_sig.dump_cs_msg,
            override=override,
            non_obf_enum_signatures_by_name=non_obf_enum_signatures_by_name,
        )
        synthetic_dump_cs_msg = _apply_field_binding_remapping(
            non_obf_sig.dump_cs_msg, override.obf_field_binding_by_non_obf_property_name
        )

        old_to_new_offset: dict[int, int] = {
            field.memory_offset: override.obf_field_binding_by_non_obf_property_name[
                field.property_name
            ].obf_memory_offset
            for field in non_obf_sig.dump_cs_msg.fields
            if field.property_name is not None
            and field.property_name in override.obf_field_binding_by_non_obf_property_name
        }
        remapped_original_offsets = frozenset(old_to_new_offset)
        override_offsets = {field_sig.field_offset for field_sig in override.field_signatures.values()}
        preserved_original_field_sigs = [
            field_sig
            for field_sig in non_obf_sig.field_signatures
            if field_sig.field_offset not in remapped_original_offsets
            and field_sig.field_offset not in override_offsets
        ]
        merged_field_sigs = bind_field_signatures_to_message_fields(
            field_signatures=preserved_original_field_sigs + list(override.field_signatures.values()),
            message=synthetic_dump_cs_msg,
        )

        result[non_obf_cls] = MessageAccessSignature(
            message_cls=non_obf_sig.message_cls,
            file_descriptor=non_obf_sig.file_descriptor,
            dump_cs_msg=synthetic_dump_cs_msg,
            function_signatures=list(override.function_signatures),
            field_signatures=merged_field_sigs,
        )
    return result


def _apply_field_binding_remapping(
    msg: DumpCSMessage,
    remapping: dict[str, FieldOverrideBinding],
) -> DumpCSMessage:
    """
    Return a new DumpCSMessage with OBF memory offsets substituted for bound fields.

    Fields whose property_name appears in remapping get their memory_offset replaced with
    the corresponding OBF offset. All other fields are unchanged. Returns the original
    object when remapping is empty.
    """
    if not remapping:
        return msg
    new_fields = [
        field.model_copy(update={"memory_offset": remapping[field.property_name].obf_memory_offset})
        if field.property_name is not None and field.property_name in remapping
        else field
        for field in msg.fields
    ]
    return msg.model_copy(update={"fields": new_fields})
