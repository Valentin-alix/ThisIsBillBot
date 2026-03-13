from collections.abc import Mapping

from DBDofusUnity.proto_mapper_assembly.interfaces.enum_mapping import (
    EnumCalledFunctionRef,
    EnumMemberGroup,
    EnumSignatureEntry,
    EnumSwitchPattern,
)
from DBDofusUnity.proto_mapper_assembly.interfaces.function_access_signature import FunctionAccessSignature


def validate_enum_signature_member_values(entry: EnumSignatureEntry) -> None:
    declared_member_values = {int(member_value) for member_value in entry.member_value_to_name}
    for switch_pattern in entry.switch_patterns:
        for member_group in switch_pattern.member_groups:
            unknown_member_values = [
                member_value
                for member_value in member_group.member_values
                if member_value not in declared_member_values
            ]
            if unknown_member_values:
                message = (
                    f"Enum signature references undeclared member values: {sorted(unknown_member_values)}"
                )
                raise ValueError(message)


def _embed_function_signature(
    called_function: EnumCalledFunctionRef,
    obf_function_signature_by_address: Mapping[str, FunctionAccessSignature],
) -> EnumCalledFunctionRef:
    return called_function.model_copy(
        update={
            "function_signature": obf_function_signature_by_address.get(called_function.function_address),
        }
    )


def build_canonical_enum_signature(
    *,
    obf_enum_signature: EnumSignatureEntry,
    value_mapping: Mapping[str, str],
    non_obf_value_to_name: Mapping[str, str],
    obf_function_signature_by_address: Mapping[str, FunctionAccessSignature],
) -> EnumSignatureEntry:
    remapped_member_value_to_name: dict[str, str] = {}
    for obf_member_value, non_obf_member_value in value_mapping.items():
        if obf_member_value not in obf_enum_signature.member_value_to_name:
            message = (
                f"Cannot canonicalize enum signature: missing obfuscated member value {obf_member_value!r}"
            )
            raise ValueError(message)
        if non_obf_member_value not in non_obf_value_to_name:
            message = (
                "Cannot canonicalize enum signature: "
                f"missing non-obfuscated member value {non_obf_member_value!r}"
            )
            raise ValueError(message)
        remapped_member_value_to_name[non_obf_member_value] = non_obf_value_to_name[non_obf_member_value]

    remapped_switch_patterns: list[EnumSwitchPattern] = []
    for switch_pattern in obf_enum_signature.switch_patterns:
        remapped_member_groups: list[EnumMemberGroup] = []
        for member_group in switch_pattern.member_groups:
            remapped_member_values = sorted(
                {
                    int(value_mapping[str(member_value)])
                    for member_value in member_group.member_values
                    if str(member_value) in value_mapping
                }
            )
            if not remapped_member_values and not member_group.is_default:
                continue
            remapped_member_groups.append(
                member_group.model_copy(
                    update={
                        "member_values": remapped_member_values,
                        "called_functions": [
                            _embed_function_signature(called_function, obf_function_signature_by_address)
                            for called_function in member_group.called_functions
                        ],
                    }
                )
            )

        remapped_switch_patterns.append(
            switch_pattern.model_copy(update={"member_groups": remapped_member_groups})
        )

    canonical_signature = EnumSignatureEntry(
        member_value_to_name={
            member_value: remapped_member_value_to_name[member_value]
            for member_value in sorted(remapped_member_value_to_name, key=int)
        },
        switch_patterns=remapped_switch_patterns,
    )
    validate_enum_signature_member_values(canonical_signature)
    return canonical_signature
